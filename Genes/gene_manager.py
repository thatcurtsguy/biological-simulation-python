from random import uniform
from biomass.entity import *
from Genes.cell_genes import *

from settings import *
import numpy as np
import hashlib

# settings
MUTATION_RATE = 0.2
MUTATION_RANGE = (-1.0, 1.0)


class ActiveGene:
    def __init__(self, name, value, weight):
        self.name = name
        self.value = value
        self.weight = weight


class Genes:
    def __init__(self, color_genes=None, trait_genes=None, active_genes=None, unique_color=None) -> None:
        self.color_genes  = color_genes  if color_genes  is not None else tuple(np.random.randint(0, 255, 3))
        self.trait_genes  = trait_genes  if trait_genes  is not None else {gene: uniform(0, 1) for gene in all_cell_trait_genes}
        self.active_genes = active_genes if active_genes is not None else {gene: self.rand_active_gene(gene) for gene in all_cell_active_genes}
        self.unique_color = unique_color if unique_color is not None else self.generate_color(self.trait_genes, self.active_genes)


    def generate_color(self, trait_genes, active_genes):
        gene_values = [value for _, value in trait_genes.items()] + [gene.value for _, gene in active_genes.items()]
        hash_string = "".join(str(value) for value in gene_values)
        hash_int = int(hashlib.sha256(hash_string.encode()).hexdigest(), 16) % (255**3)
        return (hash_int // (255**2), (hash_int // 255) % 255, hash_int % 255)


    def mutate(self):
        new_color_genes = [gene + np.random.randint(-3, 3) for gene in self.color_genes]
        new_color_genes = [max(0, min(gene, 255)) for gene in new_color_genes]
        
        new_trait_genes = {gene_name: gene + self.rand_mutation() for gene_name, gene in self.trait_genes.items()}
        new_trait_genes = {gene_name: max(0, gene) for gene_name, gene in new_trait_genes.items()}
        
        new_active_genes = {gene_name: self.mutate_active_gene(gene) for gene_name, gene in self.active_genes.items()}

        return Genes(new_color_genes, new_trait_genes, new_active_genes)
    

    def query(self, catagory, name):
        if catagory == "color":
            return self.color_genes
        
        if catagory == "trait":
            return self.trait_genes[name]
        
        if catagory == "active":
            return self.active_genes[name]


    def extract(self, active_gene : ActiveGene):
        return (active_gene.value, active_gene.weight)


    def rand_active_gene(self, name):
        return ActiveGene(name, uniform(-1, 1), uniform(-1, 1))
    
    def mutate_active_gene(self, active_gene):
        return ActiveGene(active_gene.name, active_gene.value + self.rand_mutation(), active_gene.weight + self.rand_mutation())
    
    def rand_mutation(self):
        return uniform(-MUTATION_RATE, MUTATION_RATE)


    def convert_forces_to_single_force(self, all_forces):
        total_value = 0
        total_weight = 0
        for value, weight in all_forces:
            total_value += value * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0
        else:
            return total_value / total_weight
        

    def calc_force(self, cell_close, cell_larger, cell_freind, cell_high_density):
        all_forces = []

        # Add the velocity based on the proximity of the closest life entity
        if cell_close:
            all_forces.append(self.extract(self.query("active", "cell_near")))
        else:
            all_forces.append(self.extract(self.query("active", "cell_far")))

        # Add the velocity based on the size comparison with the closest life entity
        if cell_larger:
            all_forces.append(self.extract(self.query("active", "cell_big")))
        else:
            all_forces.append(self.extract(self.query("active", "cell_small")))

        # Add the velocity based on the friendliness of the closest life entity
        if cell_freind:
            all_forces.append(self.extract(self.query("active", "cell_ally")))
        else:
            all_forces.append(self.extract(self.query("active", "cell_foe")))

        # Add the velocity based on the density of nearby life entities
        if cell_high_density:
            all_forces.append(self.extract(self.query("active", "cell_dense")))
        else:
            all_forces.append(self.extract(self.query("active", "cell_sparse")))


        return self.convert_forces_to_single_force(all_forces)



def print_genes(genes : dict, round_to=3):
    print("Genes = {")
    for gene_name in genes:
        print(f"    {gene_name} : {round(genes[gene_name], round_to)}")
    
    print("}")

