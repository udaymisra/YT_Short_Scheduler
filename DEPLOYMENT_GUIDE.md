# Deployment Guide - YouTube Shorts Crime Stories Automation

## Quick Deployment Steps

### 1. System Setup
```bash
# Navigate to project directory
cd /mnt/okcomputer/output

# Install dependencies
pip install beautifulsoup4 requests Pillow selenium apscheduler python-dotenv lxml

# Make scripts executable
chmod +x main.py test_system.py
```

### 2. Test System
```bash
# Run comprehensive system test
python test_system.py

# If all tests pass, proceed to next steps
```

### 3. Run Automation
```bash
# Option A: Run once immediately
python main.py --run

# Option B: Start daily scheduler
python main.py --schedule

# Option C: Test individual components
python main.py --test-scraper
python main.py --test-video
```

## Production Deployment

### Server Requirements
- **OS**: Linux (Ubuntu 20.04+ recommended)
- **Python**: 3.9+
- **RAM**: 2GB minimum
- **Storage**: 5GB+ free space
- **Network**: Stable internet connection

### Installation Script
```bash
#!/bin/bash
# Automated installation script

echo "Installing YouTube Shorts Crime Stories Automation..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip chromium-browser -y

# Install Python packages
pip3 install beautifulsoup4 requests Pillow selenium apscheduler python-dotenv lxml

# Create service user
sudo useradd -m -s /bin/bash crime_automation
sudo usermod -aG sudo crime_automation

# Copy files to service directory
sudo mkdir -p /opt/crime-automation
sudo cp -r * /opt/crime-automation/
sudo chown -R crime_automation:crime_automation /opt/crime-automation

echo "Installation complete!"
```

### SystemD Service
Create `/etc/systemd/system/crime-automation.service`:
```ini
[Unit]
Description=YouTube Shorts Crime Stories Automation
After=network.target

[Service]
Type=simple
User=crime_automation
WorkingDirectory=/opt/crime-automation
ExecStart=/usr/bin/python3 /opt/crime-automation/main.py --schedule
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start service:
```bash
sudo systemctl enable crime-automation
sudo systemctl start crime-automation
sudo systemctl status crime-automation
```

### Docker Deployment
Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    chromium-browser \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . /app
WORKDIR /app

# Create directories
RUN mkdir -p /app/videos /app/logs /app/temp

# Set environment variables
ENV PYTHONPATH=/app
ENV DISPLAY=:99

# Run application
CMD ["python", "main.py", "--schedule"]
```

Build and run:
```bash
docker build -t crime-automation .
docker run -d --name crime-automation crime-automation
```

## Configuration

### Environment Variables
Create `.env` file:
```env
# Optional Canva API configuration
CANVA_API_KEY=your_api_key_here
CANVA_TEMPLATE_ID=your_template_id_here

# Alert configuration
ALERT_EMAIL=your_email@example.com

# Logging
LOG_LEVEL=INFO
```

### Schedule Configuration
Edit `config.py` to modify:
- Daily execution time
- Number of stories to process
- Video quality settings
- Output directories

## Monitoring

### Log Monitoring
```bash
# View real-time logs
tail -f /mnt/okcomputer/output/logs/automation.log

# Check system status
python main.py --status

# View statistics
cat /mnt/okcomputer/output/automation_statistics.json
```

### Health Checks
The system includes:
- Automatic retry mechanisms
- Error logging
- Success rate tracking
- Email alerts (when configured)

### Performance Metrics
- Stories scraped per run
- Processing success rate
- Video creation time
- System uptime

## Maintenance

### Regular Tasks
1. **Weekly**: Check disk space and clean old files
2. **Monthly**: Review logs for recurring issues
3. **Quarterly**: Update dependencies and security patches

### Backup Strategy
```bash
# Backup configuration and logs
tar -czf backup_$(date +%Y%m%d).tar.gz /opt/crime-automation/config/ /opt/crime-automation/logs/

# Backup generated videos (optional)
tar -czf videos_backup_$(date +%Y%m%d).tar.gz /opt/crime-automation/videos/
```

### Troubleshooting

#### Common Issues

1. **Selenium WebDriver Issues**
```bash
# Install ChromeDriver manually
wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/LATEST_RELEASE_*/chromedriver_linux64.zip
sudo unzip /tmp/chromedriver.zip -d /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
```

2. **Permission Errors**
```bash
# Fix ownership
sudo chown -R crime_automation:crime_automation /opt/crime-automation/
sudo chmod -R 755 /opt/crime-automation/
```

3. **Memory Issues**
```bash
# Increase swap space
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### Log Analysis
```bash
# Check for errors
grep -i error /opt/crime-automation/logs/automation.log

# Check success rates
grep -i "completed successfully" /opt/crime-automation/logs/automation.log

# Monitor resource usage
top -p $(pgrep -f "python.*main.py")
```

## Security Considerations

### File Permissions
```bash
# Secure sensitive files
chmod 600 /opt/crime-automation/.env
chmod 755 /opt/crime-automation/main.py
chmod 644 /opt/crime-automation/config.py
```

### Network Security
- Use firewall to restrict access
- Monitor outgoing connections
- Keep system updated

### Data Privacy
- No personal data storage
- Temporary files are cleaned regularly
- Logs contain only processing metadata

## Scaling

### Horizontal Scaling
- Run multiple instances with different news sources
- Use load balancer for high availability
- Implement distributed processing

### Vertical Scaling
- Increase server resources
- Optimize scraping with async operations
- Implement caching mechanisms

## Cost Optimization

### Resource Management
- Use spot instances for cloud deployment
- Implement auto-scaling based on load
- Clean up old files regularly

### Efficiency Improvements
- Cache news sources responses
- Optimize image processing
- Use efficient data structures

## Support and Maintenance

### Documentation
- Keep README updated
- Document configuration changes
- Maintain troubleshooting guide

### Community Support
- Monitor for security updates
- Contribute improvements back
- Share best practices

---

## Quick Reference

### Essential Commands
```bash
# Start service
sudo systemctl start crime-automation

# Check status
sudo systemctl status crime-automation

# View logs
sudo journalctl -u crime-automation -f

# Restart service
sudo systemctl restart crime-automation

# Stop service
sudo systemctl stop crime-automation

# Test run
python main.py --run
```

### File Locations
- **Application**: `/opt/crime-automation/`
- **Videos**: `/opt/crime-automation/videos/`
- **Logs**: `/opt/crime-automation/logs/`
- **Config**: `/opt/crime-automation/config.py`
- **Service**: `/etc/systemd/system/crime-automation.service`

### Emergency Procedures
1. **Service Down**: Check logs, restart service
2. **No Videos Created**: Test individual components
3. **High Resource Usage**: Restart service, check for memory leaks
4. **Network Issues**: Check connectivity, firewall rules

This deployment guide provides comprehensive instructions for setting up and maintaining the YouTube Shorts Crime Stories Automation System in production environments.