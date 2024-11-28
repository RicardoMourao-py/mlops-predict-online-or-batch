# Modelo Preditivo

Após a criação do [simulador de dados](simulator/README.md), surge a necessidade de desenvolver um modelo preditivo utilizando técnicas de Machine Learning. Este processo envolve a construção de um modelo que leve em conta o histórico familiar de um paciente, incluindo variáveis relacionadas aos tipos de câncer desenvolvidos pelo paciente e por alguns de seus parentes, visando prever o resultado de um teste genético, que é a variável alvo (target).

É importante ressaltar que o resultado do teste genético pode ser "Positivo" (1) ou "Negativo" (0), e nos resultados também serão exibidas as probabilidades associadas ao teste.