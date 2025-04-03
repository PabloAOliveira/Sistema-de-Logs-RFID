# Gerenciamento de Acessos e Logs

## Descrição do Projeto
Este projeto implementa um sistema de gerenciamento de acessos de logs. Ele inclui funcionalidades de controle de colaboradores, monitoramento de acessos via RFID, armazenamento de logs e análise de dados para obter informações sobre o uso do ambiente.

## Tecnologias Utilizadas
- **Backend**: Flask (Python)
- **Banco de Dados**: SQLite
- **Frontend**: HTML, CSS e JavaScript
- **Comunicação em Tempo Real**: PubNub
- **Hardware**: Raspberry Pi com leitor RFID (MFRC522)
- **Análise de Dados**: Pandas

## Funcionalidades
### 1. API de Gerenciamento de Acessos
- **Cadastro, Edição e Exclusão de Colaboradores**
- **Registro de Logs de Acessos**
- **Consulta de Logs via API**

### 2. Sistema de RFID na Raspberry Pi
- **Leitura de Tags RFID** para autorizar acessos
- **Registro de entradas e saídas** no banco de dados
- **Feedback visual (LEDs) e sonoro (buzzer)**
- **Armazenamento temporário de acessos em caso de falha de conexão**

### 3. Interface Web
- **Cadastro e gerenciamento de colaboradores**
- **Exibição de logs em tempo real via PubNub**
- **Design responsivo e profissional**

### 4. Análise de Logs
- **Consulta de acessos por data**
- **Cálculo de tempo de permanência dos colaboradores**

## Licença
Este projeto é licenciado sob a MIT License - veja o arquivo LICENSE para mais detalhes.

## Pablo Oliveira(1134335) - Gabriela Lenz(1134940) - Patricia Lima(1136999)

