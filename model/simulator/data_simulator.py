import numpy as np
import pandas as pd
from tqdm import tqdm
import os

# Definição das constantes
tipos_cancer = [
    (-1, "Não sei se tenho"),
    (0, "Não sei onde começou"),
    (1, "Pulmão"),
    (2, "Ovário"),
    (3, "Estômago"),
    (4, "Pele"),
    (5, "Leucemia"),
    (6, "Intestino"),
    (7, "Cabeça e Pescoço"),
    (8, "Mama"),
    (9, "Próstata"),
    (10, "Tireóide"),
    (11, "Cerebral/sistema nervoso central"),
    (12, "Bexiga"),
    (13, "Linfoma"),
    (14, "Braços/pernas"),
    (15, "Outro"),
]

prob_alelos_dominantes = {
    1: 0.01,   # Pulmão
    2: 0.005,  # Ovário
    3: 0.008,  # Estômago
    4: 0.015,  # Pele
    5: 0.012,  # Leucemia
    6: 0.009,  # Intestino
    7: 0.007,  # Cabeça e Pescoço
    8: 0.006,  # Mama
    9: 0.011,  # Próstata
    10:0.013, # Tireóide
    11:0.014, # Cerebral/sistema nervoso central
    12:0.018, # Bexiga
    13:0.016, # Linfoma
    14:0.02,  # Braços/pernas
    15:0.017, # Outro
}

prob_cancer = {
    'homem': {
        1: (0.3, 0.02),  # Pulmão
        2: (0.2, 0.03),  # Ovário
        3: (0.25, 0.015),# Estômago
        4: (0.2, 0.01),  # Pele
        5: (0.3, 0.025), # Leucemia
        6: (0.2, 0.015), # Intestino
        7: (0.25, 0.02), # Cabeça e Pescoço
        8: (0.15, 0.01), # Mama
        9: (0.25, 0.015),# Próstata
        10: (0.25, 0.02),# Tireóide
        11: (0.2, 0.015),# Cerebral/sistema nervoso central
        12: (0.2, 0.015),# Bexiga
        13: (0.3, 0.025),# Linfoma
        14: (0.3, 0.02), # Braços/pernas
        15: (0.15, 0.01) # Outro
    },
    'mulher': {
        1: (0.3, 0.02),  # Pulmão
        2: (0.2, 0.03),  # Ovário
        3: (0.25, 0.015),# Estômago
        4: (0.2, 0.01),  # Pele
        5: (0.3, 0.025), # Leucemia
        6: (0.2, 0.015), # Intestino
        7: (0.25, 0.02), # Cabeça e Pescoço
        8: (0.15, 0.01), # Mama
        9: (0.25, 0.015),# Próstata
        10: (0.25, 0.02),# Tireóide
        11: (0.2, 0.015),# Cerebral/sistema nervoso central
        12: (0.2, 0.015),# Bexiga
        13: (0.3, 0.025),# Linfoma
        14: (0.3, 0.02), # Braços/pernas
        15: (0.15, 0.01) # Outro
    },
}

# Funções para manipulação genética e fenotípica
def eh_alelo_dominante(prob_alelo_dominante):
    return np.random.rand() < prob_alelo_dominante

def tem_cancer(prob_cancer):
    return np.random.rand() < prob_cancer

def gene(prob_alelo_dominante):
    return tuple(eh_alelo_dominante(prob_alelo_dominante) for _ in range(2))

def genotipo(prob_alelos_dominantes):
    return {g: gene(p) for g, p in prob_alelos_dominantes.items()}

def fenotipo(genotipo_, genero, prob_cancer):
    f = {}
    for g, genes_ in genotipo_.items():
        dominant = any(genes_)
        pR, pr = prob_cancer[genero][g]
        p_cancer = pR if dominant else pr
        f[g] = tem_cancer(p_cancer)
    return f

def heranca(genotipo_pai, genotipo_mae):
    genotipo_filho = {}
    for g in genotipo_pai:
        selecao_pai = np.random.randint(2)
        selecao_mae = np.random.randint(2)
        genotipo_filho[g] = (
            genotipo_pai[g][selecao_pai],
            genotipo_mae[g][selecao_mae],
        )
    return genotipo_filho

def genero():
    return 'homem' if np.random.randint(2) == 0 else 'mulher'

# Função heredograma atualizada para aceitar idades normalizadas como argumento
def heredograma(prob_alelos_dominantes, prob_cancer):

    genotipo_avo_paterno = genotipo(prob_alelos_dominantes)
    fenotipo_avo_paterno = fenotipo(genotipo_avo_paterno, 'homem', prob_cancer)

    genotipo_avoh_paterna = genotipo(prob_alelos_dominantes)
    fenotipo_avoh_paterna = fenotipo(genotipo_avoh_paterna, 'mulher', prob_cancer)

    genotipo_avo_materno = genotipo(prob_alelos_dominantes)
    fenotipo_avo_materno = fenotipo(genotipo_avo_materno, 'homem', prob_cancer)

    genotipo_avoh_materna = genotipo(prob_alelos_dominantes)
    fenotipo_avoh_materna = fenotipo(genotipo_avoh_materna, 'mulher', prob_cancer)

    genotipo_pai = heranca(genotipo_avo_paterno, genotipo_avoh_paterna)
    fenotipo_pai = fenotipo(genotipo_pai, 'homem', prob_cancer)

    genotipo_mae = heranca(genotipo_avo_materno, genotipo_avoh_materna)
    fenotipo_mae = fenotipo(genotipo_mae, 'mulher', prob_cancer)

    genero_paciente = genero()
    genotipo_paciente = heranca(genotipo_pai, genotipo_mae)
    fenotipo_paciente = fenotipo(genotipo_paciente, genero_paciente, prob_cancer)

    genotipo_esposo_esposa = genotipo(prob_alelos_dominantes)

    genero_filho = genero()
    genotipo_filho = heranca(genotipo_paciente, genotipo_esposo_esposa)
    fenotipo_filho = fenotipo(genotipo_filho, genero_filho, prob_cancer)

    return {
        'fenotipo_avo_paterno': fenotipo_avo_paterno,
        'fenotipo_avoh_paterna': fenotipo_avoh_paterna,
        'fenotipo_avo_materno': fenotipo_avo_materno,
        'fenotipo_avoh_materna': fenotipo_avoh_materna,
        'fenotipo_pai': fenotipo_pai,
        'fenotipo_mae': fenotipo_mae,
        'fenotipo_paciente': fenotipo_paciente,
        'fenotipo_filho': fenotipo_filho,
        'genotipo_paciente': genotipo_paciente,
        'genero_paciente': genero_paciente,
        'genero_filho': genero_filho,
    }

# Simulação de heredogramas para múltiplos pacientes
def simular_heredogramas(num_pacientes):
    pacientes = []
    for _ in tqdm(range(num_pacientes), desc="Simulando heredogramas"):
        pacientes.append(heredograma(prob_alelos_dominantes, prob_cancer))
    return pacientes

def dados_para_dataframe(pacientes):
    columns = [
        'Paciente',
        'vc_tem_lesao_atualmente',
        'idade_inicio_problema_atual',
        'onde_lesao',
        'tipo_cancer_paciente',
        'algum_filho_tem_ou_teve_cancer',
        'tipo_cancer_filho',
        'pai_tem_ou_teve_cancer',
        'tipo_cancer_pai',
        'mae_tem_ou_teve_cancer',
        'tipo_cancer_mae',
        'avo_paterno_tem_ou_teve_cancer',
        'tipo_cancer_avo_paterno',
        'avo_paterna_tem_ou_teve_cancer',
        'tipo_cancer_avo_paterna',
        'avo_materno_tem_ou_teve_cancer',
        'tipo_cancer_avo_materno',
        'avo_materna_tem_ou_teve_cancer',
        'tipo_cancer_avo_materna',
        'resultado_teste_genetico',
    ]
    
    dados = {column: [] for column in columns}

    for k, paciente in enumerate(pacientes):
        # Paciente
        nome_paciente = f'X{k+1}'
        dados['Paciente'].append(nome_paciente)

        # Você tem alguma lesão ou problema atualmente?
        fenotipo_paciente = paciente['fenotipo_paciente']
        tem_lesao=any(fenotipo_paciente.values())
        dados['vc_tem_lesao_atualmente'].append(int(tem_lesao))



        # Qual a sua idade no início do problema atual?
        dados['idade_inicio_problema_atual'].append(np.random.randint(20, 80) if tem_lesao else None)

        # Onde está sua lesão, problema atual?
        dados['onde_lesao'].append(np.random.choice(list(fenotipo_paciente.keys())) if tem_lesao else None)

        # Qual era o tipo de câncer do paciente?
        try:
            cancer_id = np.random.choice([c for c, status in fenotipo_paciente.items() if status])
        except ValueError:
            cancer_id = None
        dados['tipo_cancer_paciente'].append(cancer_id)

        # Algum filho tem ou teve câncer?
        fenotipo_filho = paciente['fenotipo_filho']
        dados['algum_filho_tem_ou_teve_cancer'].append(int(any(fenotipo_filho.values())))

        # Tipo de câncer do filho (onde começou)
        try:
            cancer_id = np.random.choice([c for c, status in fenotipo_filho.items() if status])
        except ValueError:
            cancer_id = None
        dados['tipo_cancer_filho'].append(cancer_id)

        # Seu pai teve ou têm câncer?
        fenotipo_pai = paciente['fenotipo_pai']
        dados['pai_tem_ou_teve_cancer'].append(int(any(fenotipo_pai.values())))

        # Qual o tipo de câncer do pai (onde começou)?
        try:
            cancer_id = np.random.choice([c for c, status in fenotipo_pai.items() if status])
        except ValueError:
            cancer_id = None
        dados['tipo_cancer_pai'].append(cancer_id)

        # Sua mãe teve ou têm câncer?
        fenotipo_mae = paciente['fenotipo_mae']
        dados['mae_tem_ou_teve_cancer'].append(int(any(fenotipo_mae.values())))

        # Qual o tipo de câncer da mãe (onde começou)?
        try:
            cancer_id = np.random.choice([c for c, status in fenotipo_mae.items() if status])
        except ValueError:
            cancer_id = None
        dados['tipo_cancer_mae'].append(cancer_id)

        # [avô paterno] Ele teve ou tem câncer?
        fenotipo_avo_paterno = paciente['fenotipo_avo_paterno']
        dados['avo_paterno_tem_ou_teve_cancer'].append(int(any(fenotipo_avo_paterno.values())))

        # [avô paterno] Qual tipo de câncer do avô paterno (onde começou)?
        try:
            cancer_id = np.random.choice([c for c, status in fenotipo_avo_paterno.items() if status])
        except ValueError:
            cancer_id = None
        dados['tipo_cancer_avo_paterno'].append(cancer_id)

        # [avó paterna] Ela teve ou tem câncer?
        fenotipo_avoh_paterna = paciente['fenotipo_avoh_paterna']
        dados['avo_paterna_tem_ou_teve_cancer'].append(int(any(fenotipo_avoh_paterna.values())))

        # [avó paterna] Qual tipo de câncer da avó paterna (onde começou)?
        try:
            cancer_id = np.random.choice([c for c, status in fenotipo_avoh_paterna.items() if status])
        except ValueError:
            cancer_id = None
        dados['tipo_cancer_avo_paterna'].append(cancer_id)

        # [avô materno] Ele teve ou tem câncer?
        fenotipo_avo_materno = paciente['fenotipo_avo_materno']
        dados['avo_materno_tem_ou_teve_cancer'].append(int(any(fenotipo_avo_materno.values())))

        # [avô materno] Qual tipo de câncer do avô materno (onde começou)?
        try:
            cancer_id = np.random.choice([c for c, status in fenotipo_avo_materno.items() if status])
        except ValueError:
            cancer_id = None
        dados['tipo_cancer_avo_materno'].append(cancer_id)

        # [avó materna] Ela teve ou tem câncer?
        fenotipo_avoh_materna = paciente['fenotipo_avoh_materna']
        dados['avo_materna_tem_ou_teve_cancer'].append(int(any(fenotipo_avoh_materna.values())))

        # [avó materna] Qual tipo de câncer da avó materna (onde começou)?
        try:
            cancer_id = np.random.choice([c for c, status in fenotipo_avoh_materna.items() if status])
        except ValueError:
            cancer_id = None
        dados['tipo_cancer_avo_materna'].append(cancer_id)

        # Resultado do teste genético
        genotipo_paciente = paciente['genotipo_paciente']
        has_mutation = [any(r) for r in genotipo_paciente.values()]
        dados['resultado_teste_genetico'].append(int(any(has_mutation)))

    df = pd.DataFrame(dados)
    
    return df

pacientes_simulados = simular_heredogramas(10000)
dados_simulados = dados_para_dataframe(pacientes_simulados)

def exportar_para_csv(dados, pasta, nome_arquivo):
    if not os.path.exists(pasta):
        os.makedirs(pasta)
    caminho_arquivo = os.path.join(pasta, nome_arquivo)
    dados.to_csv(caminho_arquivo, index=False)
    print(f"Dados exportados para: {caminho_arquivo}")

exportar_para_csv(dados_simulados, "../data", "dados_simulados.csv")