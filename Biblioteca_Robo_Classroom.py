from __future__ import print_function
import os.path
from google.colab import drive
import os
from google.colab import files
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import date
import datetime
import numpy as np
import math
import pandas as pd
from tqdm.notebook import tqdm
from datetime import datetime as dt


class robo_classroom(object):

  # Variáveis da Classe
  servico = []
  Data = []
  course_id = []
  topic_id = []
  coursework_id = []

  def __int__(self):
      iago = 1
      # self.servico = self.Criar_Servico(Caminho_Credentials, Caminho_Token)

  def main(self, caminho_drive='Robo_Classroom',Datas = [],Mes_inicial = [],Ano_inicial=[], Horario_inicio =[]):
      print('Montando o Drive')
      caminho_pasta = self.conectar_drive(caminho_drive)
      Caminho_Credentials = caminho_pasta + '/credentials.json'
      Caminho_Token = caminho_pasta + '/token.json'
      self.servico = self.Criar_Servico(Caminho_Credentials, Caminho_Token)
      print('Serviço Realizado!')

      self.Escolher_Curso()
      print(f'\n 0 - Criar Chamada! \n 1 - Criar Tarefas Alunos \n 2 - Responder Chamada \n 3 - Verossemelhança \n 4 - Resumo de Notas')
      escolha = int(input("Digite o Indice do que deseja fazer :"))

      if escolha == 0:
        if len(Datas) ==0:
          print(f'Os valores das Datas, Mes_inicial, Ano_inicio e Horário_Inicio dos Trabalhos não foi enviada. \n Siga o seguinte exemplo: \n Horario_Inicio = [21, 19] \n Dias = [5, 7, 12] \n Mes_Inicial = 4 \n Ano_Inicial = 2023 \n Marcato.main(caminho_drive, Dias, Mes_Inicial, Ano_Inicial, Horario_Inicio)')
        else:
          self.Criar_Chamada(Dias, Mes_inicial, Ano_inicial, Horario_inicio)
      if escolha == 1:

        print(f'Siga o seguinte exemplo: \n Horario_Inicio = [14] \n Horario_Fim = 16 \n Dias = [5, 7, 12] \n Mes_Inicial = 4 \n Ano_Inicial = 2023 \n Dia_Tarefa = "Sexta-feira" \n objeto.Criar_atividades(Horario_Inicio,Horario_Fim,Dias,Mes_Inicial,Ano_Inicial,Dia_Tarefa,Numero_apresentadores = 2)')


      if escolha == 2:
        self.Retornar_Chamada()
      if escolha == 3:
        self.Enviar_Verossimilhanca()
      if escolha == 4:
        self.fim_periodo()

  def conectar_drive(self, caminho_drive):
      # Montar o Google Drive no Colab com o nome gdrive

      drive.mount('/content/gdrive')

      # O comando abaixo mostra qual diretório você está trabalhando momento.
      # print( os.getcwd() )

      Caminho_Onde_Salvar = 'gdrive/My Drive/' + caminho_drive

      return Caminho_Onde_Salvar

  def Criar_Servico(self, Caminho_Credentials='credentials.json', Caminho_Token='token.json'):
      SCOPES = [
          'https://www.googleapis.com/auth/classroom.courses',
          'https://www.googleapis.com/auth/classroom.rosters',
          'https://www.googleapis.com/auth/classroom.coursework.students',
          'https://www.googleapis.com/auth/classroom.topics.readonly'
      ]
      creds = None
      if os.path.exists(Caminho_Token):
          creds = Credentials.from_authorized_user_file(Caminho_Token, SCOPES)
      # If there are no (valid) credentials available, let the user log in.
      if not creds or not creds.valid:
          if creds and creds.expired and creds.refresh_token:
              creds.refresh(Request())
          else:
              flow = InstalledAppFlow.from_client_secrets_file(
                  Caminho_Credentials, SCOPES)
              creds = flow.run_local_server(port=0)
          # Save the credentials for the next run
          with open(Caminho_Token, 'w') as token:
              token.write(creds.to_json())

      try:
          service = build('classroom', 'v1', credentials=creds)
          return service
      except:
          print('Erro: Não criou serviço')

  def Escolher_Curso(self):

      # Listagem de todas as atividades do curso
      course = self.servico.courses().list(pageSize=40,courseStates='ACTIVE').execute()
      # print(course)

      # # Impressão da lista de Cursos com seus índices
      for index, curso in enumerate(course['courses']):
          print(f"{index}: {curso['name']}")

      # # Solicitação do índice dos Cursos selecionada pelo usuário
      Course_index = int(input("Digite o Indice do Curso :"))
      self.course_id = course['courses'][Course_index]['id']
      # print(self.course_id)

  def Criar_Chamada(self, Dias, Mes_Inicial, Ano_Inicial, Horario_inicio):

      topicos = self.servico.courses().topics().list(courseId=self.course_id).execute()

      # print(topicos)

      # Listagem de todas as Tópicos do curso
      Topics = self.servico.courses().topics().list(courseId=self.course_id).execute()

      # # Impressão da lista de Cursos com seus índices
      for index, curso in enumerate(Topics['topic']):
          print(f"{index}: {curso['name']}")

      # # Solicitação do índice dos Cursos selecionada pelo usuário
      topic_index = int(input("Digite o Indice do Tópico de chamada :"))
      self.topic_id = Topics['topic'][topic_index]['topicId']
      # print(self.topic_id)
      Dias_Sem = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-Feira', 'Sexta-feira', 'Sábado', 'Domingo']

      Meses = [Mes_Inicial]
      Anos = [Ano_Inicial]

      for i in range(1, len(Dias)):
          if Dias[i - 1] > Dias[i]:
              Mes_Inicial = Mes_Inicial + 1

          Meses.append(Mes_Inicial)

      for i in range(1, len(Dias)):

          if Meses[i - 1] > Meses[i]:
              Ano_Inicial = Ano_Inicial + 1

          Anos.append(Ano_Inicial)

      # print(Anos)
      # print(Meses)
      # print(Dias)

      Dias_Semanas = []
      for i in range(len(Horario_inicio)):
          # print(i)
          data = date(year=Anos[i], month=Meses[i], day=Dias[i])
          indice_da_semana = data.weekday()
          dia_da_semana = Dias_Sem[indice_da_semana]
          Dias_Semanas.append(dia_da_semana)

      service = self.servico

      for i in range(len(Dias)):
          data = date(year=Anos[i], month=Meses[i], day=Dias[i])
          indice_da_semana = data.weekday()
          dia_da_semana = Dias_Sem[indice_da_semana]
          if dia_da_semana == Dias_Semanas[0]:
              Aux = 0
          elif dia_da_semana == Dias_Semanas[1]:
              Aux = 1
          # print('Data:',data,', Dia da Semana:',dia_da_semana)

          data_tarefa_Publicada = datetime.datetime(Anos[i], Meses[i], Dias[i], Horario_inicio[Aux], 0,
                                                    0) + datetime.timedelta(hours=3)
          data_tarefa_Entrega = datetime.datetime(Anos[i], Meses[i], Dias[i], Horario_inicio[Aux], 0,
                                                  0) + datetime.timedelta(hours=5)

          # Formata a data e horário para o formato aceito pela API
          data_tarefa_Publicada_str = data_tarefa_Publicada.isoformat() + 'Z'
          Titulo = 'Frequência ' + str(Dias[i]) + '/' + str(Meses[i]) + '/' + str(Anos[i]) + ' (' + dia_da_semana + ')'
          # print(Titulo)
          tarefa = {'title': Titulo,
                    'state': 'DRAFT',
                    'dueDate': {'year': Anos[i], 'month': data_tarefa_Entrega.month, 'day': data_tarefa_Entrega.day},
                    'dueTime': {'hours': data_tarefa_Entrega.hour, 'minutes': data_tarefa_Entrega.minute},
                    'scheduledTime': data_tarefa_Publicada_str,
                    'maxPoints': 1,
                    'workType': 'MULTIPLE_CHOICE_QUESTION',
                    'submissionModificationMode': 'MODIFIABLE_UNTIL_TURNED_IN',
                    'multipleChoiceQuestion': {'choices': ['Presente']},
                    'assigneeMode': 'ALL_STUDENTS',
                    'topicId': self.topic_id}

          # Cria a tarefa
          try:
              tarefa_criada = service.courses().courseWork().create(courseId=self.course_id, body=tarefa).execute()
              print(f'Tarefa criada: {tarefa_criada.get("title")}')
          except HttpError as error:
              print(f'Ocorreu um erro ao criar a tarefa: {error}')

  def Escolher_Atividade(self,Qual_trabalho):
    # Listagem de todas as atividades do curso
    courseworks = self.servico.courses().courseWork().list(courseId=self.course_id).execute()
    data_obj = dt.strptime(self.Data, '%d/%m/%Y')
    Dias_Sem = [' (Segunda-feira)', ' (Terça-feira)', ' (Quarta-feira)', ' (Quinta-feira)', ' (Sexta-feira)', ' (Sabado)', ' (Domingo)']
    indice_dia = data_obj.weekday()
    dia_semana = Dias_Sem[indice_dia]

    # Nome_Atividade = 'Aluno '+str(Qual_trabalho)+' - ' + self.Data + ' (Sexta-feira)'
    Nome_Atividade = 'Aluno '+ str(Qual_trabalho)+' - ' + self.Data + dia_semana

    for i in range(len(courseworks['courseWork'])):
        # Verificar se o nome contém "Aluno 1 - Data (Quarta-Feira)" e se a data corresponde ao dia informado pelo usuário
        if Nome_Atividade == courseworks['courseWork'][i]['title']:
            # Retornar o coursework_id da atividade encontrada
            coursework_id = courseworks['courseWork'][i]['id']
            # print(f"Curso: {course['name']}\nAtividade: {coursework['title']}\nCoursework ID: {coursework['id']}")

    if 'coursework_id' in locals() or 'coursework_id' in globals():
        return coursework_id
    else:
        self.Data = input('Data não encontrada. Informe o dia da atividade (ex: 22/3/2023): ')
        coursework_id = self.Escolher_Atividade(Qual_trabalho)

  def Pegar_Nota(self,Qual_trabalho):

      self.coursework_id = self.Escolher_Atividade(Qual_trabalho)
      # Listagem dos alunos matriculados no curso
      students = self.servico.courses().students().list(courseId=self.course_id).execute()

      # Coleta dos IDs dos alunos
      ids_alunos = [student['userId'] for student in students['students']]

      coursework = self.servico.courses().courseWork().list(courseId=self.course_id).execute()
      submissions = self.servico.courses().courseWork().studentSubmissions().list(courseId=self.course_id,courseWorkId=self.coursework_id).execute()

      # Coleta das respostas dos alunos
      respostas = []
      nomes_alunos = []
      Ids_alunos = []
      i = 1
      print('Lendo Notas Trabalho ',str(Qual_trabalho))
      for submission in tqdm(submissions['studentSubmissions']):
          # print('Lendo aluno ' + str(i))
          i = i+1
          submission_id = submission['id']
          Ids_alunos.append(submission['id'])
          submission1 = self.servico.courses().courseWork().studentSubmissions().get(courseId=self.course_id, courseWorkId=self.coursework_id, id=submission_id).execute()
          try:
              respostas.append(int(submission1['shortAnswerSubmission']['answer']))
          except:
              respostas.append(-1)
          aluno = self.servico.userProfiles().get(userId=submission1['userId']).execute()
          nomes_alunos.append(aluno['name']['fullName'])

      respostas = np.array(respostas)

      return respostas,nomes_alunos,Ids_alunos

  def Calcular_notas_Vero(self,respostas1,nomes_alunos1,respostas2,nomes_alunos2):

    conjunto1 = set([idx for idx, val in enumerate(respostas1) if val == -100])
    conjunto2 = set([idx for idx, val in enumerate(respostas2) if val == -100])

    Apresentador_Aux = list(conjunto1.union(conjunto2))
    # Apresentador_Aux2 = np.where(respostas2 == -100)
    # print(Apresentador_Aux[0])

    Aux1 = int(input('O aluno ' + nomes_alunos1[Apresentador_Aux[0]] + ' foi o 1º ou 2º aluno?'))

    Aux = np.where(respostas1 >= 0)

    if Aux1 == 1:
        Apresentador1 = Apresentador_Aux[0]
        Apresentador2 = Apresentador_Aux[1]
    else:
        Apresentador1 = Apresentador_Aux[1]
        Apresentador2 = Apresentador_Aux[0]

    desvio = 20

    Nota_Professor_1 = int(input('Nota Aluno 1:'))
    Nota_Professor_2 = int(input('Nota Aluno 2:'))

    Notas_Alunos1 = []
    Notas_Alunos2 = []
    for i in range(len(respostas1)):
        if respostas1[i] == -1:
            Notas_Alunos1.append(0)
        else:
            Notas_Alunos1.append(math.ceil(100 * np.exp(-(respostas1[i] - Nota_Professor_1) ** 2 / (2 * desvio ** 2))))

    Notas_Alunos1[Apresentador1] = math.ceil((Nota_Professor_1 + np.mean(respostas1[Aux])) / 2)
    Notas_Alunos1[Apresentador2] = math.ceil((Nota_Professor_2 + np.mean(respostas2[Aux])) / 2)

    for i in range(len(respostas2)):
        if respostas2[i] == -1:
            Notas_Alunos2.append(0)
        else:
            Notas_Alunos2.append(math.ceil(100 * np.exp(-(respostas2[i] - Nota_Professor_2) ** 2 / (2 * desvio ** 2))))

    Notas_Alunos2[Apresentador1] = math.ceil((Nota_Professor_1 + np.mean(respostas1[Aux])) / 2)
    Notas_Alunos2[Apresentador2] = math.ceil((Nota_Professor_2 + np.mean(respostas2[Aux])) / 2)


    d1 = {'Nomes': nomes_alunos1,
        'Nota dada': respostas1,
        'Nota do Aluno': Notas_Alunos1
        }
    df1 = pd.DataFrame(data=d1)
    df1_N = df1.sort_values('Nomes')


    print(df1_N)

    d2 = {'Nomes': nomes_alunos2,
        'Nota dada': respostas2,
        'Nota do Aluno': Notas_Alunos2
        }
    df2 = pd.DataFrame(data=d2)
    df2_N = df2.sort_values('Nomes')

    print(df2_N)

    return df1, df2, Notas_Alunos1, Notas_Alunos2

  def Enviar_Notas_aos_Alunos(self,Notas,Qual_trabalho,Draft_or_Published=0):

    coursework_id = self.Escolher_Atividade(Qual_trabalho)
    students = self.servico.courses().students().list(courseId=self.course_id).execute()
    i = 0

    submissions = self.servico.courses().courseWork().studentSubmissions().list(courseId=self.course_id,courseWorkId=coursework_id).execute()
    print('Enviando Notas da Apresentação', str(Qual_trabalho))
    # for student in students['students']:
    for submission in tqdm(submissions['studentSubmissions']):
        submission_id = submission['id']
        submission1 = self.servico.courses().courseWork().studentSubmissions().get(courseId=self.course_id, courseWorkId=coursework_id, id=submission_id).execute()


        if Draft_or_Published == 0:
            body = {
                'draftGrade': Notas[i],
                'userId': submission['userId']
            }
            i = i+1
            self.servico.courses().courseWork().studentSubmissions().patch(courseId=self.course_id, courseWorkId=coursework_id, id=submission1['id'], updateMask='draftGrade', body=body).execute()
        else:
            body = {
                'assignedGrade': Notas[i],
                'draftGrade': Notas[i],
                'userId': submission['userId']
            }
            i = i+1
            self.servico.courses().courseWork().studentSubmissions().patch(courseId=self.course_id, courseWorkId=coursework_id, id=submission['id'], updateMask='assignedGrade,draftGrade', body=body).execute()


        # print('Enviado Nota Aluno ',str(i))
    print('Notas enviadas com sucesso!')

  def Enviar_Verossimilhanca(self):

    # self.servico = self.Criar_Serviço()
    # Perguntar o dia da atividade
    self.Data = input('Informe o dia da atividade (ex: 22/3/2023): ')
    Draft_or_Published = int(input('[0] - Rascunho ou [1] - Publicar: '))

    respostas1,nomes_alunos1,Ids_alunos1 = self.Pegar_Nota(Qual_trabalho=1)
    respostas2,nomes_alunos2,Ids_alunos2 = self.Pegar_Nota(Qual_trabalho=2)

    df1,df2,Notas_Alunos1,Notas_Alunos2 = self.Calcular_notas_Vero(respostas1=respostas1,nomes_alunos1=nomes_alunos1,
                                                        respostas2=respostas2,nomes_alunos2=nomes_alunos2)

    self.Enviar_Notas_aos_Alunos(Notas=Notas_Alunos1,Qual_trabalho=1,Draft_or_Published=Draft_or_Published)
    self.Enviar_Notas_aos_Alunos(Notas=Notas_Alunos2,Qual_trabalho=2,Draft_or_Published=Draft_or_Published)

  def Escolher_Chamada(self):
      courseworks = self.servico.courses().courseWork().list(courseId=self.course_id).execute()
      # Nome_Atividade = 'Aluno ' + str(Qual_trabalho) + ' - ' + self.Data + ' (Quarta-feira)'
      self.Data = input('Informe o dia da Chamada (ex: 22/3/2023): ')
      dia, mes, ano = map(int, self.Data.split("/"))
      data = date(year=ano, month=mes, day=dia)
      Dias_Sem = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-Feira', 'Sexta-feira', 'Sábado', 'Domingo']
      indice_da_semana = data.weekday()
      dia_da_semana = Dias_Sem[indice_da_semana]
      Nome_Atividade = 'Frequência ' + self.Data + ' (' + dia_da_semana + ')'

      for i in range(len(courseworks['courseWork'])):
          # Verificar se o nome contém "Aluno 1 - Data (Quarta-Feira)" e se a data corresponde ao dia informado pelo usuário
          if Nome_Atividade == courseworks['courseWork'][i]['title']:
              # Retornar o coursework_id da atividade encontrada
              coursework_id = courseworks['courseWork'][i]['id']
              # print(f"Curso: {course['name']}\nAtividade: {coursework['title']}\nCoursework ID: {coursework['id']}")

      if 'coursework_id' in locals() or 'coursework_id' in globals():
          return coursework_id
      else:
          self.Data = input('Data não encontrada. Informe o dia da atividade (ex: 22/3/2023): ')
          coursework_id = self.Escolher_Atividade(Qual_trabalho)

  def Retornar_Chamada(self):
    Presente = 0
    Ausente = 0
    self.coursework_id = self.Escolher_Chamada()

    students = self.servico.courses().students().list(courseId=self.course_id).execute()

    # Coleta dos IDs dos alunos
    ids_alunos = [student['userId'] for student in students['students']]

    coursework = self.servico.courses().courseWork().list(courseId=self.course_id).execute()
    submissions = self.servico.courses().courseWork().studentSubmissions().list(courseId=self.course_id,courseWorkId=self.coursework_id).execute()
    i = 1
    for submission in tqdm(submissions['studentSubmissions']):
        # print('Respondendo Aluno: ', i)
        i = i+1
        submission_id = submission['id']
        submission1 = self.servico.courses().courseWork().studentSubmissions().get(courseId=self.course_id,
                                                                                    courseWorkId=self.coursework_id,
                                                                                    id=submission_id).execute()
        DRAFT = 0
        try:
            if submission1['multipleChoiceSubmission']['answer'] == 'Presente':
                Presente = Presente + 1
                if DRAFT == 0:
                  body = {
                          'assignedGrade': 1,
                          'draftGrade': 1,
                          'userId': submission['userId']
                  }
                  self.servico.courses().courseWork().studentSubmissions().patch(courseId=self.course_id,
                                                                                    courseWorkId=self.coursework_id,
                                                                                    id=submission['id'],
                                                                                    updateMask='assignedGrade,draftGrade',
                                                                                    body=body).execute()
                else:


                  body = {
                          'draftGrade': 1,
                          'userId': submission['userId']
                  }
                  self.servico.courses().courseWork().studentSubmissions().patch(courseId=self.course_id,
                                                                                    courseWorkId=self.coursework_id,
                                                                                    id=submission['id'],
                                                                                    updateMask='draftGrade',
                                                                                    body=body).execute()
        except:
            Ausente = Ausente + 1

            if DRAFT == 0:
              body = {
                'assignedGrade': 0,
                'draftGrade': 0,
                'userId': submission['userId']
            }
              self.servico.courses().courseWork().studentSubmissions().patch(courseId=self.course_id,
                                                                            courseWorkId=self.coursework_id,
                                                                            id=submission['id'],
                                                                            updateMask='assignedGrade,draftGrade',
                                                                            body=body).execute()
            else:
              body = {
                'draftGrade': 0,
                'userId': submission['userId']
            }
              self.servico.courses().courseWork().studentSubmissions().patch(courseId=self.course_id,
                                                                            courseWorkId=self.coursework_id,
                                                                            id=submission['id'],
                                                                            updateMask='draftGrade',
                                                                            body=body).execute()


    print('Presentes:',Presente,' - Ausentes:',Ausente)


    iago = 1

  def Criar_atividades(self,Horario_Inicio,Horario_Fim,Dias,Mes,Ano,Dia_Tarefa = 'Quarta-feira',Numero_apresentadores = 2):
    #A entrada é o Horario inicial e final da aula.
    #Os dias que serão as atividades.
    #Mes Inicial da atividade
    #Ano Inicial do Curso

    Dias_Sem = ['Segunda-feira','Terça-feira','Quarta-feira','Quinta-Feira','Sexta-feira','Sábado','Domingo']


    self.Escolher_Curso()

    Meses = [Mes]

    for i in range(1,len(Dias)):
      if Dias[i-1] > Dias[i]:
          Mes = Mes + 1

      Meses.append(Mes)

    # Listagem de todas as Tópicos do curso
    Topics = self.servico.courses().topics().list(courseId=self.course_id).execute()

    # # Impressão da lista de Cursos com seus índices
    for index, curso in enumerate(Topics['topic']):
      print(f"{index}: {curso['name']}")

    # # Solicitação do índice dos Cursos selecionada pelo usuário
    topic_index = int(input("Digite o Indice do Tópico de Atividade :"))
    self.topic_id = Topics['topic'][topic_index]['topicId']


    for i in range(len(Dias)):

      data = date(year=Ano, month=Meses[i], day=Dias[i])
      indice_da_semana = data.weekday()
      dia_da_semana = Dias_Sem[indice_da_semana]
      if dia_da_semana == Dia_Tarefa:
        # print('Data:',data,', Dia da Semana:',dia_da_semana)

        data_tarefa_Publicada = datetime.datetime(2023, Meses[i], Dias[i], Horario_Inicio[0], 0, 0) + datetime.timedelta(hours=3)
        data_tarefa_Entrega = datetime.datetime(2023, Meses[i], Dias[i], Horario_Inicio[0], 0, 0) + datetime.timedelta(hours=5)

        # Formata a data e horário para o formato aceito pela API
        data_tarefa_Publicada_str = data_tarefa_Publicada.isoformat() + 'Z'
        for j in range(Numero_apresentadores):
          Titulo = 'Aluno ' + str(j + 1) + ' - '  + str(Dias[i])+'/'+str(Meses[i])+'/'+str(Ano)+ ' ('+dia_da_semana+')'
          print(Titulo)
          Descricao = 'Qual a nota para o ' + str(j + 1) + 'º apresentador do dia ' + str(Dias[i])+'/'+str(Meses[i])+'/'+str(Ano) + '. Nota entre 0 e 100! O apresentador deve responder com -100 para ambas as atividades do dia!',
          tarefa = {'title': Titulo,
                    'state': 'DRAFT',
                    'description': Descricao[0],
                    'dueDate': {'year': Ano, 'month': data_tarefa_Entrega.month, 'day': data_tarefa_Entrega.day},
                    'dueTime': {'hours': data_tarefa_Entrega.hour, 'minutes': data_tarefa_Entrega.minute},
                    'scheduledTime': data_tarefa_Publicada_str,
                    'maxPoints': 100,
                    'workType': 'SHORT_ANSWER_QUESTION',
                    'submissionModificationMode': 'MODIFIABLE_UNTIL_TURNED_IN',
                    'assigneeMode': 'ALL_STUDENTS',
                    'topicId': self.topic_id}


          # Cria a tarefa
          try:
              tarefa_criada = self.servico.courses().courseWork().create(courseId=self.course_id, body=tarefa).execute()
              print(f'Tarefa criada: {tarefa_criada.get("title")}')
          except HttpError as error:
              print(f'Ocorreu um erro ao criar a tarefa: {error}')

  def fim_periodo(self):

    # Pegar a lista de alunos
    students = []
    request = self.servico.courses().students().list(courseId=self.course_id, pageSize=1000)

    while request is not None:
      response = request.execute()
      students.extend(response.get('students', []))
      request = self.servico.courses().students().list_next(previous_request=request, previous_response=response)

    student_names = []
    student_id = []
    # Mapear userId para nome de estudante

    student_grades = {}
    for i in range(len(students)):
        student_names.append(students[i]['profile']['name']['fullName'])
        student_id.append(students[i]['profile']['id'])

    # Pegar a lista de trabalhos do curso
    course_works = self.servico.courses().courseWork().list(courseId=self.course_id).execute()

    # Inicializar um dicionário para armazenar as notas
    student_grades = {student_id: [] for student_id in student_id}

    # Inicializar a lista de notas máximas
    max_points = []

    # Data atual
    current_date = date.today()

    # Iterar sobre cada trabalho
    for work in course_works['courseWork']:
        # Converter a data de entrega do trabalho para um objeto date
        due_date = date(year=work['dueDate']['year'], month=work['dueDate']['month'], day=work['dueDate']['day'])

        # Verificar se o prazo de entrega já passou
        if due_date <= current_date:
            # Adicionar a nota máxima à lista
            max_points.append(work['maxPoints'])

            # Pegar as submissões para este trabalho
            submissions = self.servico.courses().courseWork().studentSubmissions().list(
                courseId=self.course_id, courseWorkId=work['id']).execute()

            # Iterar sobre cada submissão
            for submission in submissions['studentSubmissions']:
                # Pegar a nota, se houver
                if 'assignedGrade' in submission:
                    student_grades[submission['userId']].append(submission['assignedGrade'])

    # Agora você tem o mapeamento de nomes e notas para cada aluno
    # for student_id, grades in student_grades.items():
    #     print(f"Student {student_names[student_id]}: {grades}")
    Nomes = []
    Nota_Chamada = []
    Nota_Apresentacao = []
    Nota_Trabalhos = []

    # Valor_Chamada = 1
    # Valor_Apresentacao = 100
    # Valor_Trabalhos = 100000
    Valor_Chamada = int(input("Digite o valor da Atividade de Chamada [Padrão:1]:"))
    Valor_Apresentacao = int(input("Digite o valor da Atividade de Apresentacao [Padrão:100]:"))
    Valor_Trabalhos = int(input("Digite o valor da Atividade de Apresentacao [Padrão:100000]:"))

    Aux_Chamada = np.where(np.array(max_points) == Valor_Chamada)[0]
    Aux_Apresentacao = np.where(np.array(max_points) == Valor_Apresentacao)[0]
    Aux_Trabalhos = np.where(np.array(max_points) == Valor_Trabalhos)[0]

    Num_Trabalhos_Removidos = int(input("Digite a quantidade de trabalhos de menor nota que será retirado [Padrão: 3]:"))
    # Num_Trabalhos_Removidos = 3


    for student, grades in student_grades.items():
        Aux = student_id.index(student)
        print("Calculando Nota do Aluno:", student_names[Aux])
        Nomes.append(student_names[Aux])
        Notas = np.array(student_grades[student])
        try:
            Notas_Apresentacao = Notas[Aux_Apresentacao]
            Notas_Chamadas = Notas[Aux_Chamada]
            Notas_Trabalhos = Notas[Aux_Trabalhos]
        except:
            print("Alguma Nota Não foi lançada!")
            break

        Notas_Apresentacao.sort()
        Notas_Apresentacao = Notas_Apresentacao[Num_Trabalhos_Removidos:]
        Nota_Apresentacao_media = np.mean(Notas_Apresentacao)/Valor_Apresentacao*100
        Nota_Apresentacao.append(Nota_Apresentacao_media)

        Notas_Chamadas.sort()
        Notas_Chamadas = Notas_Chamadas[Num_Trabalhos_Removidos:]
        Nota_Chamadas_media = np.mean(Notas_Chamadas)/Valor_Chamada*100
        Nota_Chamada.append(Nota_Chamadas_media)

        Notas_Trabalhos.sort()
        Notas_Trabalhos = Notas_Trabalhos[Num_Trabalhos_Removidos:]
        Notas_Trabalhos_media = np.mean(Notas_Trabalhos)/Valor_Trabalhos*100
        Nota_Trabalhos.append(Notas_Trabalhos_media)
        iago = 1

    # Criar o DataFrame
    df = pd.DataFrame({
        'Nomes': Nomes,
        'Nota Chamada': Nota_Chamada,
        'Nota Apresentacao': Nota_Apresentacao,
        'Nota Trabalhos': Nota_Trabalhos
    })

    # pd.set_option('display.max_columns', None)
    # pd.set_option('display.max_rows', None)
    # Imprimir o DataFrame
    display(df)

