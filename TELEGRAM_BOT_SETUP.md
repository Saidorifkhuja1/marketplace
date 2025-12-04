# Telegram Bot Setup on PythonAnywhere

## Overview
This guide explains how to run the Telegram bot on PythonAnywhere using long-running tasks or scheduled tasks.

## Prerequisites
- PythonAnywhere account with your Django project deployed
- Telegram Bot Token (already in `tg_bot/tokens.py`)
- API URL pointing to your PythonAnywhere domain

## Setup Steps

### 1. Update Bot Configuration

**File:** `tg_bot/tokens.py`

Ensure your configuration is correct:
```python
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
API_URL = "https://qrmenu.pythonanywhere.com"  # Use HTTPS for production
```

### 2. Install Dependencies

SSH into PythonAnywhere and activate your virtual environment:

```bash
# Activate venv
source /home/qrmenu/venv/bin/activate

# Install requirements (if not already done)
pip install -r /home/qrmenu/marketplace/requirements.txt
```

### 3. Option A: Using PythonAnywhere Long-Running Tasks (Recommended)

**Advantages:**
- Runs continuously
- Automatic restart on failure
- Easy to manage from dashboard

**Steps:**

1. Go to **PythonAnywhere Dashboard** → **Tasks**
2. Click **Create a new task**
3. Enter the command:
   ```bash
   /home/qrmenu/venv/bin/python /home/qrmenu/marketplace/run_bot.py
   ```
4. Set it to run **Always** or on a schedule
5. Click **Create**

The bot will now run continuously in the background.

### 4. Option B: Using Scheduled Tasks (Alternative)

If long-running tasks aren't available:

1. Go to **PythonAnywhere Dashboard** → **Scheduled tasks**
2. Create a new task to run every minute:
   ```bash
   /home/qrmenu/venv/bin/python /home/qrmenu/marketplace/run_bot.py
   ```

### 5. Monitor Bot Logs

**View logs in PythonAnywhere:**

```bash
# SSH into PythonAnywhere
ssh qrmenu@ssh.pythonanywhere.com

# View task logs
tail -f /var/log/qrmenu_pythonanywhere_com_task_*.log

# Or check the Tasks page in dashboard for output
```

### 6. Verify Bot is Running

Test the bot by:

1. **Start the bot in Telegram:**
   - Open Telegram
   - Search for your bot (e.g., @YourBotName)
   - Send `/start` command
   - You should see a welcome message

2. **Check logs:**
   - Look for "Starting bot..." message
   - Check for successful API calls to your Django backend

### 7. Troubleshooting

**Bot not responding:**
- Check if task is running in PythonAnywhere dashboard
- Verify `BOT_TOKEN` is correct
- Check `API_URL` is accessible
- Review logs for errors

**API connection errors:**
- Ensure Django app is running
- Check `ALLOWED_HOSTS` includes your domain
- Verify CORS settings allow bot requests
- Test API manually: `curl https://qrmenu.pythonanywhere.com/user/auth/telegram/`

**Module not found errors:**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`
- Check Python path in task command

### 8. Configuration Files

**Bot Configuration:**
- `tg_bot/tokens.py` - Bot token and API URL
- `tg_bot/bot.py` - Bot handlers and logic
- `run_bot.py` - Bot runner script

**Django Configuration:**
- `core/settings.py` - Django settings
- `user/views.py` - Authentication endpoints

### 9. API Endpoints Used by Bot

The bot uses these Django endpoints:

- **POST** `/user/auth/telegram/` - Authenticate user via Telegram
  - Request: Telegram auth data
  - Response: JWT tokens and user info

### 10. Security Notes

- ✅ Bot token is stored securely in `tokens.py`
- ✅ API uses HTTPS for production
- ✅ CSRF protection configured for PythonAnywhere domain
- ✅ CORS allows bot requests

### 11. Monitoring and Maintenance

**Regular checks:**
- Monitor bot task status in PythonAnywhere dashboard
- Check logs for errors
- Test `/start` command weekly
- Monitor API response times

**Restart bot:**
- Go to Tasks page
- Click "Stop" then "Start"
- Or wait for automatic restart on failure

### 12. Production Checklist

- [ ] Bot token is correct
- [ ] API URL uses HTTPS
- [ ] Django app is deployed and running
- [ ] ALLOWED_HOSTS includes your domain
- [ ] CORS settings allow bot requests
- [ ] Task is running in PythonAnywhere
- [ ] Logs show successful startup
- [ ] Bot responds to `/start` command
- [ ] User registration works end-to-end

## Support

For issues:
1. Check PythonAnywhere task logs
2. Review Django error logs
3. Test API endpoints manually
4. Verify network connectivity

## Next Steps

After bot is running:
1. Create a Telegram Mini App for the marketplace
2. Add more bot commands (/menu, /search, etc.)
3. Implement order notifications
4. Add payment integration
