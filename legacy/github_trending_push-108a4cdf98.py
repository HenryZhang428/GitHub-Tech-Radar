#!/usr/bin/env python3
"""
GitHub热榜定时推送脚本
每天指定时间获取GitHub热榜数据并发送邮件通知
"""

import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import json
from datetime import datetime, timedelta

def get_github_trending(since='weekly', language=''):
    """获取GitHub热榜数据"""
    # 计算日期范围
    if since == 'daily':
        since_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    elif since == 'weekly':
        since_date = (datetime.now() - timedelta(weeks=1)).strftime('%Y-%m-%d')
    elif since == 'monthly':
        since_date = (datetime.now() - timedelta(weeks=4)).strftime('%Y-%m-%d')
    else:
        since_date = (datetime.now() - timedelta(weeks=1)).strftime('%Y-%m-%d')
    
    # 构建搜索查询
    query = f'created:>{since_date}'
    if language:
        query += f' language:{language}'
    
    # 使用GitHub搜索API获取热门项目
    url = f'https://api.github.com/search/repositories?q={requests.utils.quote(query)}&sort=stars&order=desc&per_page=10'
    response = requests.get(url)
    data = response.json()
    
    return data.get('items', [])

def send_email(subject, body, to_email):
    """发送邮件通知"""
    # 配置邮件服务器
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'your_email@gmail.com'
    smtp_password = 'your_email_password'
    
    # 创建邮件
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = to_email
    msg['Subject'] = subject
    
    # 添加邮件正文
    msg.attach(MIMEText(body, 'html'))
    
    # 发送邮件
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_username, to_email, msg.as_string())
        server.quit()
        print('邮件发送成功')
    except Exception as e:
        print(f'邮件发送失败: {e}')

def generate_report(repos):
    """生成HTML格式的报告"""
    html = '<html><body>'
    html += '<h1>GitHub热榜每日报告</h1>'
    html += f'<p>报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>'
    html += '<ul>'
    
    for repo in repos:
        html += '<li>'
        html += f'<h3><a href='{repo['html_url']}' target='_blank'>{repo['name']}</a></h3>'
        html += f'<p>描述: {repo['description'] or '无描述'}</p>'
        html += f'<p>星标数: {repo['stargazers_count']}</p>'
        html += f'<p>编程语言: {repo['language'] or '未知'}</p>'
        html += '</li>'
    
    html += '</ul>'
    html += '</body></html>'
    
    return html

def main():
    """主函数"""
    # 配置
    since = 'weekly'  # daily, weekly, monthly
    language = ''  # 空表示所有语言
    to_email = 'your_email@example.com'
    push_time = '09:00'  # 每天推送时间
    
    while True:
        # 获取当前时间
        now = datetime.now()
        current_time = now.strftime('%H:%M')
        
        # 如果当前时间等于推送时间
        if current_time == push_time:
            # 获取GitHub热榜数据
            repos = get_github_trending(since, language)
            
            # 生成报告
            report = generate_report(repos)
            
            # 发送邮件
            subject = f'GitHub热榜报告 - {now.strftime('%Y-%m-%d')}'
            send_email(subject, report, to_email)
            
            # 等待一天
            time.sleep(86400)
        else:
            # 等待1分钟
            time.sleep(60)

if __name__ == '__main__':
    main()