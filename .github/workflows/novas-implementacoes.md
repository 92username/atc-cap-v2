As Tabelas 5, 6 e 8 definem as fórmulas e os casos para o cálculo do $t_{ij}$ (Separação entre Duas Operações de Pouso ou Decolagem), que é o intervalo de tempo mínimo possível entre operações sucessivas. Já as Tabelas 7 e 9 listam os dados de entrada (coletados ou fornecidos) necessários para aplicar essas fórmulas nos exemplos de pouso e decolagem, respectivamente.

As variáveis necessárias para executar os cálculos contidos nas tabelas 5 a 9 são as seguintes:

### Variáveis Fundamentais para o Cálculo de $t_{ij}$ (Tabelas 5, 6 e 8)

O $t_{ij}$ é o elemento central para determinar o tempo mínimo de separação entre uma aeronave precedente do tipo “i” e uma aeronave subsequente do tipo “j”. As variáveis matemáticas essenciais são:

*   **$C$ (Comprimento da Aproximação Final):** A distância entre o Fixo de Aproximação Final (FAF) e a cabeceira da pista.
*   **$S_{ij}$ (Separação Mínima Entre Aeronaves):** A separação mínima na aproximação final exigida entre a aeronave da frente (tipo “i”) e a aeronave que a segue (tipo “j”), levando em conta a esteira de turbulência entre elas.
*   **$V_i$ e $V_j$ (Velocidade na Aproximação Final):** A velocidade da aeronave do tipo “i” (aeronave da frente) e a velocidade da aeronave do tipo “j” (aeronave que a segue) percorrendo o comprimento da aproximação final.
*   **$O_i$ (Ocupação de Pista):** O tempo de ocupação da pista da aeronave do tipo “i” (aeronave da frente).

O cálculo do $t_{ij}$ (Tabelas 5, 6 e 8) adota o maior valor entre o tempo necessário para manter a separação mínima de esteira de turbulência no ar e o tempo de ocupação da pista da aeronave precedente ($O_i$).

### Dados de Entrada (Tabelas 7 e 9)

As Tabelas 7 e 9 detalham os dados coletados ou fornecidos para as operações de pouso (Tabela 7) e decolagem (Tabela 9) que são usados nos cálculos de $t_{ij}$ e, subsequentemente, dos coeficientes $\alpha$ e $\beta$:

| Variável | Descrição/Exemplo (Pouso - Tabela 7) | Descrição/Exemplo (Decolagem - Tabela 9) |
| :--- | :--- | :--- |
| **Categoria** | Classificação da aeronave (Ex: H, M, L, que se referem à esteira de turbulência). | Classificação da aeronave (Ex: H, M, L). |
| **Mix** | A distribuição percentual da frota de aeronaves em operação (probabilidade de ocorrência $p_i$ e $p_j$). | A distribuição percentual da frota de aeronaves em operação (probabilidade de ocorrência $p_i$ e $p_j$). |
| **Vel. Aprox. (Kt)** | A velocidade de aproximação final por categoria (usado para $V_i$ e $V_j$). | - |
| **Vel. Decolagem (Kt)** | - | A velocidade de decolagem por categoria. |
| **Ocupação de Pistas (seg)** | Tempo médio de ocupação de pista por categoria durante o pouso (usado para $O_i$). | Tempo médio de ocupação de pista por categoria durante a decolagem (usado para TOPD). |
| **Comprimento da Aprox. Final (C)** | A distância entre o FAF e a cabeceira da pista. | - |