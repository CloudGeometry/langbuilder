# Corporate Authentication Setup Guide

Этот гайд поможет настроить корпоративную аутентификацию с Google Workspace для ActionBridge.

## Возможности системы

✅ **Google Workspace Integration** - проверка пользователей через Directory API  
✅ **Multi-session support** - сохранение полной мульти-сессии  
✅ **RBAC via Google Groups** - автоматическое назначение ролей по группам  
✅ **Domain verification** - только сотрудники компании могут войти  
✅ **Multi-company support** - легко адаптируется для разных компаний  

## Шаг 1: Настройка Google Cloud Project

### 1.1 Создайте Google Cloud Project
1. Откройте [Google Cloud Console](https://console.cloud.google.com)
2. Создайте новый проект для ActionBridge
3. Активируйте следующий API:
   - **Admin SDK API** (для проверки пользователей через Google Workspace Directory)
   
   **Примечание**: для OAuth аутентификации отдельный API не требуется, достаточно создать OAuth 2.0 Client ID в следующем шаге.

### 1.2 Создайте Service Account
1. Идите в IAM & Admin > Service Accounts
2. Создайте новый Service Account: `actionbridge-workspace-reader`
3. Скачайте JSON ключ
4. Сохраните как `/app/secrets/google-service-account.json`

### 1.3 Создайте OAuth 2.0 Client
1. Идите в APIs & Services > Credentials
2. Создайте OAuth 2.0 Client ID:
   - Application type: Web application
   - Authorized redirect URIs: `https://your-domain.com/oauth/google/callback`
3. Сохраните Client ID и Client Secret

## Шаг 2: Настройка Google Workspace

### 2.1 Domain-wide Delegation
1. В Google Admin Console перейдите в Security > API Controls
2. Добавьте ваш Service Account Client ID
3. Предоставьте следующие OAuth Scopes:
   ```
   https://www.googleapis.com/auth/admin.directory.user.readonly
   https://www.googleapis.com/auth/admin.directory.group.readonly
   ```

### 2.2 Создайте группы для RBAC
Создайте следующие группы в Google Admin:
- `actionbridge-admin@actionbridge.com` - администраторы
- `actionbridge-users@actionbridge.com` - обычные пользователи
- `engineering@actionbridge.com` - инженеры (user роль)
- `management@actionbridge.com` - менеджмент (admin роль)

## Шаг 3: Конфигурация ActionBridge

### 3.1 Создайте corporate_config.json
```json
{
  "company_name": "ActionBridge",
  "google_workspace": {
    "domain": "actionbridge.com",
    "admin_email": "admin@actionbridge.com",
    "service_account_key_file": "/app/secrets/google-service-account.json"
  },
  "require_workspace_verification": true,
  "auto_approve_verified_users": true,
  "default_role_for_verified_users": "user",
  "oauth_client_id": "YOUR_CLIENT_ID",
  "oauth_client_secret": "YOUR_CLIENT_SECRET",
  "group_to_role_mapping": {
    "actionbridge-admin@actionbridge.com": "admin",
    "actionbridge-users@actionbridge.com": "user",
    "engineering@actionbridge.com": "user", 
    "management@actionbridge.com": "admin"
  }
}
```

### 3.2 Environment Variables
```bash
# Corporate Configuration
CORPORATE_AUTH_CONFIG=/app/corporate_config.json

# Google OAuth (от Google Cloud Console)
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=https://your-domain.com/oauth/google/callback

# Enable OAuth
ENABLE_OAUTH_SIGNUP=true
OAUTH_ALLOWED_DOMAINS=*  # Или ограничьте доменом: actionbridge.com
```

## Шаг 4: Тестирование

### 4.1 Проверка подключения к Workspace
```python
import asyncio
from backend.open_webui.utils.corporate_auth import test_workspace_connection

# Тест подключения
result = asyncio.run(test_workspace_connection("/app/corporate_config.json"))
print(result)
```

### 4.2 Тест авторизации
1. Перейдите на `https://your-domain.com`
2. Нажмите "Sign in with Google"  
3. Выберите аккаунт из корпоративного домена
4. Убедитесь что пользователь создался с правильной ролью

## Для других компаний

Для адаптации под другую компанию:

1. Скопируйте `corporate_config_template.json`
2. Замените:
   - `COMPANY_NAME` → название компании
   - `company.com` → домен компании  
   - Группы в `group_to_role_mapping`
3. Создайте свой Service Account в Google Cloud
4. Настройте Domain-wide Delegation

## Возможные ошибки

### "Service not available"
- Проверьте что Service Account JSON файл существует
- Проверьте права доступа к файлу

### "User not found in workspace" 
- Убедитесь что пользователь существует в Google Workspace
- Проверьте что домен в конфигурации правильный

### "Access denied"
- Проверьте Domain-wide Delegation в Google Admin
- Убедитесь что у admin_email есть права на Directory API

### "OAuth error"
- Проверьте Client ID и Client Secret
- Убедитесь что redirect URI правильный

## Безопасность

🔒 **Service Account** имеет только права на чтение Directory API  
🔒 **Hosted Domain** ограничивает OAuth только корпоративными аккаунтами  
🔒 **Workspace Verification** проверяет каждого пользователя через API  
🔒 **Multi-session** поддерживается без компромиссов безопасности  

## Логи

Для диагностики включите debug логи:
```bash
SRC_LOG_LEVELS={"MAIN": "DEBUG"}
```

Система будет логировать:
- Результаты проверки пользователей в Workspace
- Маппинг групп на роли
- Ошибки подключения к API