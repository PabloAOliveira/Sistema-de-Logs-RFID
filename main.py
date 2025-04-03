import time
import csv
import requests
import datetime
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

GPIO.setwarnings(False)  
GPIO.cleanup()  
GPIO.setmode(GPIO.BCM)

LED_VERDE = 2
LED_VERMELHO = 3
BUZZER = 4
GPIO.setup(LED_VERDE, GPIO.OUT)
GPIO.setup(LED_VERMELHO, GPIO.OUT)
GPIO.setup(BUZZER, GPIO.OUT)

buzzer_pwm = GPIO.PWM(BUZZER, 1000)
buzzer_pwm.start(0)

API_URL = "http://10.1.25.108:5000/logs"

colaboradores = {
    428077549992: "Pablo",
    690782802875: "Patricia",
    112233445: "Gabriela Alemoa"
}

registro_presenca = {}
tentativas_nao_autorizadas = {}
tentativas_invasao = {}

leitorRFid = SimpleMFRC522()

def tocar_buzzer(frequencia, duracao):
    buzzer_pwm.ChangeFrequency(frequencia)
    buzzer_pwm.ChangeDutyCycle(50)
    time.sleep(duracao)
    buzzer_pwm.ChangeDutyCycle(0)

def acionar_led_e_buzzer(led, tempo, frequencia_som):
    GPIO.output(led, GPIO.HIGH)
    if frequencia_som:
        tocar_buzzer(frequencia_som, tempo)
    time.sleep(tempo)
    GPIO.output(led, GPIO.LOW)

def piscar_led_e_buzzer_vermelho(vezes, intervalo=0.3):
    for _ in range(vezes):
        GPIO.output(LED_VERMELHO, GPIO.HIGH)
        tocar_buzzer(2000, intervalo)
        GPIO.output(LED_VERMELHO, GPIO.LOW)
        time.sleep(intervalo)

def enviar_log(tag_id, nome, tipo):
    data = {
        "colaborador_id": tag_id, 
        "nome": nome,
        "tipo": tipo,
        "horario": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    for tentativa in range(3):  
        try:
            response = requests.post(API_URL, json=data, timeout=5)
            if response.status_code == 201:
                print(f"Log enviado: {data}")
                return
            else:
                print(f"Erro ao enviar log ({tentativa + 1}/3): {response.text}")
        except requests.RequestException as e:
            print(f"Tentativa {tentativa + 1}/3 falhou: {e}")
        time.sleep(2)
    print("Falha ao conectar com a API após 3 tentativas.")

def salvar_registros():
    with open("registro_acessos.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Nome", "Horário de Entrada"])
        for tag_id, horario in registro_presenca.items():
            writer.writerow([tag_id, colaboradores.get(tag_id, "Desconhecido"), time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(horario))])
    
    with open("tentativas_nao_autorizadas.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Nome", "Tentativas"])
        for tag_id, info in tentativas_nao_autorizadas.items():
            writer.writerow([tag_id, info['nome'], info['tentativas']])

try:
    while True:
        print("Aguardando leitura da tag...")
        tag_id, text = leitorRFid.read()
        tag_id = int(tag_id)

        if tag_id in colaboradores:
            nome = colaboradores[tag_id]
            if tag_id not in registro_presenca:
                print(f"Bem-vindo, {nome}")
                registro_presenca[tag_id] = time.time()
                acionar_led_e_buzzer(LED_VERDE, 0.5, 1000)
                enviar_log(tag_id, nome, "entrada")
            else:
                print(f"Saída registrada para {nome}")
                del registro_presenca[tag_id]  
                acionar_led_e_buzzer(LED_VERDE, 0.5, 1000)
                enviar_log(tag_id, nome, "saida")
        
        elif text and text.strip():
            nome = text.strip()
            print(f"Você não tem acesso a este projeto, {nome}")
            acionar_led_e_buzzer(LED_VERMELHO, 0.5, 500)
            enviar_log(tag_id, nome, "tentativa_nao_autorizada")
        
        else:
            print("Identificação não encontrada!")
            piscar_led_e_buzzer_vermelho(10)
            if tag_id in tentativas_invasao:
                tentativas_invasao[tag_id] += 1
            else:
                tentativas_invasao[tag_id] = 1
        
        time.sleep(2)

except KeyboardInterrupt:
    print("\nEncerrando o programa e salvando registros...")
    salvar_registros()
    buzzer_pwm.stop()
    GPIO.cleanup()
    print("Registros salvos com sucesso!")
