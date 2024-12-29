from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path
import pickle
import base64
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from email.mime.text import MIMEText
import textwrap
import time
import csv
from zoneinfo import ZoneInfo

class GmailChecker:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.modify', 'https://www.googleapis.com/auth/gmail.send']
        self.creds = None
        self.service = None
        self.current_messages = []
        self.hours_filter = None
        self.search_term = None

    def authenticate(self):
        """Maneja el proceso de autenticación con Gmail."""
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)
        
        self.service = build('gmail', 'v1', credentials=self.creds)

    def set_hours_filter(self, hours):
        """Establece el filtro de horas para los correos."""
        self.hours_filter = hours

    def set_search_term(self, term):
        """Establece el término de búsqueda para filtrar correos."""
        self.search_term = term.lower() if term else None

    def get_unread_messages(self):
        """Obtiene los detalles de los correos no leídos con filtros aplicados."""
        try:
            result = self.service.users().messages().list(
                userId='me',
                q='is:unread'
            ).execute()
            
            messages = result.get('messages', [])
            self.current_messages = []
            
            if not messages:
                return []
                
            email_details = []
            now = datetime.now(ZoneInfo("UTC"))
            
            for message in messages:
                msg = self.service.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='full'
                ).execute()
                
                headers = msg['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'Sin asunto')
                from_header = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Desconocido')
                date_header = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
                
                try:
                    date_obj = parsedate_to_datetime(date_header)
                    if date_obj.tzinfo is None:
                        date_obj = date_obj.replace(tzinfo=ZoneInfo("UTC"))
                    formatted_date = date_obj.astimezone().strftime("%d/%m/%Y %H:%M")
                    
                    if self.hours_filter:
                        time_diff = now - date_obj
                        if time_diff > timedelta(hours=self.hours_filter):
                            continue
                except Exception as e:
                    formatted_date = date_header
                    continue
                
                if self.search_term:
                    if not (self.search_term in subject.lower() or 
                           self.search_term in from_header.lower()):
                        continue
                
                snippet = msg.get('snippet', '')
                
                self.current_messages.append(message['id'])
                email_details.append({
                    'id': message['id'],
                    'from': from_header,
                    'subject': subject,
                    'date': formatted_date,
                    'snippet': snippet
                })
                
            return email_details
            
        except Exception as e:
            print(f'\033[91mError: {str(e)}\033[0m')
            return None

    def get_email_thread(self, message_id):
        """Obtiene los detalles del hilo de correo para responder."""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'Sin asunto')
            from_header = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')
            
            from_email = from_header.split('<')[-1].replace('>', '') if '<' in from_header else from_header
            
            thread_id = message.get('threadId', '')
            
            return {
                'subject': subject,
                'from_email': from_email,
                'thread_id': thread_id
            }
        except Exception as e:
            print(f'\033[91mError al obtener detalles del correo: {str(e)}\033[0m')
            return None

    def send_reply(self, message_id, reply_text):
        """Envía una respuesta al correo seleccionado."""
        try:
            thread_info = self.get_email_thread(message_id)
            if not thread_info:
                return False, "No se pudo obtener la información del correo"
            
            if not thread_info['subject'].lower().startswith('re:'):
                subject = f"Re: {thread_info['subject']}"
            else:
                subject = thread_info['subject']
            
            message = MIMEText(reply_text)
            message['to'] = thread_info['from_email']
            message['subject'] = subject
            message['In-Reply-To'] = message_id
            message['References'] = message_id
            
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            self.service.users().messages().send(
                userId='me',
                body={
                    'raw': raw,
                    'threadId': thread_info['thread_id']
                }
            ).execute()
            
            return True, "Respuesta enviada exitosamente"
        except Exception as e:
            return False, f"Error al enviar la respuesta: {str(e)}"

    def mark_as_read(self, message_ids):
        """Marca los correos seleccionados como leídos."""
        success = True
        try:
            for msg_id in message_ids:
                try:
                    self.service.users().messages().modify(
                        userId='me',
                        id=msg_id,
                        body={'removeLabelIds': ['UNREAD']}
                    ).execute()
                    print(f"\033[92m✔ Correo marcado como leído exitosamente\033[0m")
                    time.sleep(0.5)
                except Exception as e:
                    print(f"\033[91m❌ Error al marcar correo {msg_id}: {str(e)}\033[0m")
                    success = False
            return success
        except Exception as e:
            print(f'\033[91mError general: {str(e)}\033[0m')
            return False

    def export_to_csv(self, emails, selected):
        """Exporta los correos seleccionados a un archivo CSV."""
        if not selected:
            return False, "No hay correos seleccionados para exportar"
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'correos_exportados_{timestamp}.csv'
            
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Remitente', 'Asunto', 'Fecha', 'Contenido'])
                
                for i in selected:
                    if 1 <= i <= len(emails):
                        email = emails[i-1]
                        writer.writerow([
                            email['from'],
                            email['subject'],
                            email['date'],
                            email['snippet']
                        ])
            
            return True, filename
        except Exception as e:
            return False, f"Error al exportar: {str(e)}"

def print_email_details_with_selection(emails, selected, hours_filter=None, search_term=None):
    """Imprime los correos mostrando cuáles están seleccionados."""
    if not emails:
        print("\n\033[93m📭 No tienes correos sin leer", end="")
        if hours_filter:
            print(f" en las últimas {hours_filter} horas", end="")
        if search_term:
            print(f" que coincidan con '{search_term}'", end="")
        print("\033[0m")
        return
        
    print(f"\n\033[1m📬 Tienes {len(emails)} correos sin leer", end="")
    if hours_filter:
        print(f" en las últimas {hours_filter} horas", end="")
    if search_term:
        print(f" que coinciden con '{search_term}'", end="")
    print(":\033[0m\n")
    
    for i, email in enumerate(emails, 1):
        print("\033[94m" + "━" * 80 + "\033[0m")
        status = "[✓]" if i in selected else "[ ]"
        print(f"\033[1m{status} #{i}\033[0m")
        print(f"\033[1m👤 De:\033[0m {email['from']}")
        print(f"\033[1m📋 Asunto:\033[0m {email['subject']}")
        print(f"\033[1m🕒 Fecha:\033[0m {email['date']}")
        print(f"\033[1m💌 Contenido:\033[0m")
        wrapped_content = textwrap.fill(email['snippet'], width=75)
        print(f"{wrapped_content}\n")

def print_menu():
    """Imprime el menú de opciones."""
    print("\n\033[1m📋 Comandos disponibles:\033[0m")
    print("\033[96m├─\033[0m Número del correo (ej: 1) : Marcar/Desmarcar correo individual")
    print("\033[96m├─\033[0m a                         : Seleccionar todos los correos")
    print("\033[96m├─\033[0m d                         : Deseleccionar todos los correos")
    print("\033[96m├─\033[0m m                         : Marcar seleccionados como leídos")
    print("\033[96m├─\033[0m e                         : Exportar seleccionados a CSV")
    print("\033[96m├─\033[0m r                         : Refrescar lista de correos")
    print("\033[96m├─\033[0m h <número>               : Filtrar por horas (ej: h 24)")
    print("\033[96m├─\033[0m s <texto>                : Buscar en remitente/asunto")
    print("\033[96m├─\033[0m p <número>               : Responder a un correo específico")
    print("\033[96m├─\033[0m c                         : Limpiar filtros")
    print("\033[96m└─\033[0m q                         : Salir")

def handle_user_input(emails, checker):
    """Maneja la interacción del usuario de manera más intuitiva."""
    selected = set()
    
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print_email_details_with_selection(
            emails, 
            selected, 
            checker.hours_filter, 
            checker.search_term
        )
        print_menu()
        print(f"\n\033[93mCorreos seleccionados: {len(selected)}\033[0m")
        
        command = input("\n\033[1m💡 Ingresa un comando:\033[0m ").lower().strip()
        
        if command == 'q':
            return None
        elif command == 'a':
            selected = set(range(1, len(emails) + 1))
            print("\n\033[92m✔ Todos los correos seleccionados\033[0m")
            input("Presiona Enter para continuar...")
        elif command == 'd':
            selected.clear()
            print("\n\033[93m✔ Selección limpiada\033[0m")
            input("Presiona Enter para continuar...")
        elif command == 'r':
            return 'refresh'
        elif command == 'c':
            checker.set_hours_filter(None)
            checker.set_search_term(None)
            return 'refresh'
        elif command == 'e':
            success, result = checker.export_to_csv(emails, selected)
            if success:
                print(f"\n\033[92m✔ Correos exportados exitosamente a '{result}'\033[0m")
            else:
                print(f"\n\033[91m❌ {result}\033[0m")
            input("Presiona Enter para continuar...")
        elif command.startswith('h '):
            try:
                hours = int(command.split()[1])
                if hours > 0:
                    checker.set_hours_filter(hours)
                    return 'refresh'
                else:
                    print("\n\033[91m❌ El número de horas debe ser positivo\033[0m")
                    input("Presiona Enter para continuar...")
            except (ValueError, IndexError):
                print("\n\033[91m❌ Formato inválido. Usa 'h <número>'\033[0m")
                input("Presiona Enter para continuar...")
        elif command.startswith('s '):
            search_term = command[2:].strip()
            if search_term:
                checker.set_search_term(search_term)
                return 'refresh'
            else:
                print("\n\033[91m❌ Término de búsqueda vacío\033[0m")
                input("Presiona Enter para continuar...")
        elif command.startswith('p '):
            try:
                num = int(command.split()[1])
                if 1 <= num <= len(emails):
                    print("\n\033[1m📝 Escribe tu respuesta (termina con una línea que contenga solo '.')\033[0m")
                    reply_lines = []
                    while True:
                        line = input()
                        if line == '.':
                            break
                        reply_lines.append(line)
                    
                    reply_text = '\n'.join(reply_lines)
                    if reply_text.strip():
                        success, message = checker.send_reply(emails[num-1]['id'], reply_text)
                        if success:
                            print(f"\n\033[92m✔ {message}\033[0m")
                        else:
                            print(f"\n\033[91m❌ {message}\033[0m")
                    else:
                        print("\n\033[91m❌ La respuesta está vacía\033[0m")
                    input("Presiona Enter para continuar...")
                else:
                    print("\n\033[91m❌ Número de correo inválido\033[0m")
                    input("Presiona Enter para continuar...")
            except (ValueError, IndexError):
                print("\n\033[91m❌ Formato inválido. Usa 'p <número>'\033[0m")
                input("Presiona Enter para continuar...")
        elif command == 'm':
            if not selected:
                print("\n\033[93m⚠️  No hay correos seleccionados\033[0m")
                input("Presiona Enter para continuar...")
                continue
                
            print(f"\n\033[93mMarcando {len(selected)} correos como leídos...\033[0m")
            ids_to_mark = [emails[i-1]['id'] for i in selected]
            
            if checker.mark_as_read(ids_to_mark):
                print("\n\033[92m✔ Correos marcados como leídos exitosamente\033[0m")
                input("Presiona Enter para continuar...")
                return 'refresh'
            else:
                print("\n\033[91m❌ Hubo algunos errores al marcar los correos\033[0m")
                input("Presiona Enter para continuar...")
                return 'refresh'
        else:
            try:
                num = int(command)
                if 1 <= num <= len(emails):
                    if num in selected:
                        selected.remove(num)
                        print(f"\n\033[93m✔ Correo #{num} deseleccionado\033[0m")
                    else:
                        selected.add(num)
                        print(f"\n\033[92m✔ Correo #{num} seleccionado\033[0m")
                    input("Presiona Enter para continuar...")
                else:
                    print("\n\033[91m❌ Número de correo inválido\033[0m")
                    input("Presiona Enter para continuar...")
            except ValueError:
                print("\n\033[91m❌ Comando no reconocido\033[0m")
                input("Presiona Enter para continuar...")

def main():
    checker = GmailChecker()
    checker.authenticate()
    
    while True:
        emails = checker.get_unread_messages()
        
        if emails is None:
            print('\033[91mNo se pudieron obtener los correos no leídos.\033[0m')
            break
            
        if not emails and not (checker.hours_filter or checker.search_term):
            print("\n\033[93m📭 No tienes correos sin leer\033[0m")
            break
            
        result = handle_user_input(emails, checker)
        
        if result is None:  # Usuario eligió salir
            break
        elif result == 'refresh':  # Usuario marcó correos como leídos o solicitó refrescar
            continue  # Vuelve al inicio del ciclo para obtener la lista actualizada

if __name__ == '__main__':
    main()