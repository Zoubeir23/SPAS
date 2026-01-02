# Checklist de Déploiement en Production - SPAS Authentication

## Avant le Déploiement

### Configuration de Sécurité

- [ ] **SECRET_KEY**: Générer une nouvelle clé aléatoire
  ```python
  python -c "import secrets; print(secrets.token_urlsafe(50))"
  ```

- [ ] **DEBUG**: Mettre à `False` dans `.env`
  ```env
  DEBUG=False
  ```

- [ ] **ALLOWED_HOSTS**: Configurer les domaines autorisés
  ```env
  ALLOWED_HOSTS=spas.votredomaine.com,api.spas.votredomaine.com
  ```

- [ ] **CORS_ALLOWED_ORIGINS**: Limiter aux domaines frontend
  ```env
  CORS_ALLOWED_ORIGINS=https://spas.votredomaine.com
  ```

### Base de Données

- [ ] **PostgreSQL**: Utiliser une instance production (non locale)
- [ ] **DB_PASSWORD**: Mot de passe fort et unique
- [ ] **Backups**: Configurer les sauvegardes automatiques
- [ ] **SSL/TLS**: Activer les connexions chiffrées
- [ ] **Connection pooling**: Vérifier CONN_MAX_AGE=600

### Redis

- [ ] **Redis**: Utiliser instance production (non locale)
- [ ] **Protection**: Activer mot de passe Redis
  ```bash
  # Dans redis.conf
  requirepass votre_mot_de_passe_fort
  ```
- [ ] **Persistence**: Activer RDB ou AOF
- [ ] **Maxmemory**: Configurer limite mémoire
- [ ] **SSL/TLS**: Activer si disponible

### Email

- [ ] **Provider**: Configurer service email production (SendGrid, SES, etc.)
- [ ] **Authentification**: Utiliser App Password ou API Key
- [ ] **SPF/DKIM**: Configurer records DNS pour deliverability
- [ ] **From Email**: Utiliser domaine vérifié
- [ ] **Rate Limits**: Vérifier limites du provider

### JWT et Tokens

- [ ] **Token Lifetime**: Ajuster selon besoins sécurité
  ```env
  JWT_ACCESS_TOKEN_LIFETIME=15  # 15 minutes recommandé
  JWT_REFRESH_TOKEN_LIFETIME_DAYS=7  # 7 jours max recommandé
  ```

- [ ] **Token Rotation**: Vérifier activé
  ```python
  SIMPLE_JWT = {
      'ROTATE_REFRESH_TOKENS': True,
      'BLACKLIST_AFTER_ROTATION': True,
  }
  ```

### Rate Limiting

- [ ] **Ajuster limites** selon trafic attendu
  ```python
  'DEFAULT_THROTTLE_RATES': {
      'login': '10/minute',      # Ajuster selon besoin
      'register': '5/day',       # Ajuster selon besoin
      'password_reset': '5/hour',
  }
  ```

- [ ] **Monitoring**: Configurer alertes sur rate limit hits

### SSL/HTTPS

- [ ] **Certificat SSL**: Installer certificat valide (Let's Encrypt recommandé)
- [ ] **HTTPS**: Rediriger tout trafic HTTP vers HTTPS
- [ ] **HSTS**: Vérifier activé dans settings production
  ```python
  SECURE_HSTS_SECONDS = 31536000
  SECURE_HSTS_INCLUDE_SUBDOMAINS = True
  SECURE_HSTS_PRELOAD = True
  ```

### Logging et Monitoring

- [ ] **Logs**: Configurer rotation des logs
  ```bash
  # Utiliser logrotate ou équivalent
  /var/log/spas/*.log {
      daily
      rotate 30
      compress
      delaycompress
      notifempty
  }
  ```

- [ ] **Monitoring**: Configurer Sentry, DataDog, ou équivalent
- [ ] **Alertes**: Email/SMS pour erreurs critiques
- [ ] **Métriques**: CPU, mémoire, Redis, DB

### Performance

- [ ] **Gunicorn**: Configurer workers appropriés
  ```bash
  # Formule: (2 x CPU cores) + 1
  gunicorn config.wsgi:application \
    --workers 5 \
    --bind 0.0.0.0:8000 \
    --timeout 120
  ```

- [ ] **Static Files**: Servir via CDN ou Nginx
- [ ] **Cache**: Vérifier Redis cache fonctionne
- [ ] **Database Indexes**: Vérifier présence sur champs clés

### Sécurité Avancée

- [ ] **Firewall**: Limiter accès DB et Redis aux IPs autorisées
- [ ] **VPC**: Utiliser réseau privé virtuel si cloud
- [ ] **Secrets**: Utiliser vault (AWS Secrets Manager, etc.)
- [ ] **Dependencies**: Scanner vulnérabilités
  ```bash
  pip install safety
  safety check
  ```

- [ ] **Headers HTTP**: Vérifier headers sécurité
  ```python
  SECURE_BROWSER_XSS_FILTER = True
  SECURE_CONTENT_TYPE_NOSNIFF = True
  X_FRAME_OPTIONS = 'DENY'
  ```

## Déploiement

### Pre-déploiement

- [ ] **Tests**: Exécuter tous les tests
  ```bash
  python manage.py test
  ```

- [ ] **Migrations**: Vérifier migrations sont à jour
  ```bash
  python manage.py makemigrations --check
  python manage.py migrate --plan
  ```

- [ ] **Static Files**: Collecter fichiers statiques
  ```bash
  python manage.py collectstatic --noinput
  ```

- [ ] **Dependencies**: Vérifier requirements.txt à jour

### Déploiement Initial

- [ ] **Environment**: Créer fichier `.env` production
- [ ] **Database**: Créer base de données
  ```bash
  createdb spas_prod -O spas_user
  ```

- [ ] **Redis**: Démarrer instance Redis
- [ ] **Migrations**: Appliquer migrations
  ```bash
  python manage.py migrate
  ```

- [ ] **Superuser**: Créer admin initial
  ```bash
  python manage.py createsuperuser
  ```

- [ ] **Permissions**: Vérifier permissions fichiers/dossiers

### Services

- [ ] **Gunicorn**: Configurer service systemd
  ```ini
  [Unit]
  Description=SPAS Gunicorn daemon
  After=network.target

  [Service]
  User=spas
  Group=www-data
  WorkingDirectory=/path/to/spas/backend
  Environment="PATH=/path/to/venv/bin"
  ExecStart=/path/to/venv/bin/gunicorn config.wsgi:application --workers 5 --bind unix:/run/gunicorn.sock

  [Install]
  WantedBy=multi-user.target
  ```

- [ ] **Celery**: Configurer worker et beat
  ```bash
  celery -A config worker -l info
  celery -A config beat -l info
  ```

- [ ] **Nginx**: Configurer reverse proxy
  ```nginx
  server {
      listen 443 ssl http2;
      server_name api.spas.votredomaine.com;

      ssl_certificate /path/to/cert.pem;
      ssl_certificate_key /path/to/key.pem;

      location / {
          proxy_pass http://unix:/run/gunicorn.sock;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto $scheme;
      }

      location /static/ {
          alias /path/to/spas/backend/staticfiles/;
      }
  }
  ```

## Post-Déploiement

### Validation

- [ ] **Health Check**: Tester endpoint /api/auth/me/
- [ ] **Registration**: Tester inscription complète
- [ ] **Login**: Tester connexion
- [ ] **Email**: Vérifier emails reçus
- [ ] **Tokens**: Tester refresh tokens
- [ ] **Rate Limiting**: Vérifier protection active
- [ ] **Logs**: Vérifier logs générés correctement

### Tests de Charge

- [ ] **Load Testing**: Tester avec wrk, locust, ou k6
  ```bash
  # Exemple avec k6
  k6 run --vus 100 --duration 60s load_test.js
  ```

- [ ] **Stress Testing**: Identifier point de rupture
- [ ] **Spike Testing**: Tester pics de trafic soudains
- [ ] **Endurance Testing**: Tester 24h+ continu

### Monitoring Initial

- [ ] **Uptime**: Configurer monitoring uptime (UptimeRobot, etc.)
- [ ] **Logs**: Vérifier logs sur 24h
- [ ] **Métriques**: Analyser CPU, mémoire, DB
- [ ] **Erreurs**: Vérifier aucune erreur 500
- [ ] **Performance**: Mesurer temps de réponse

### Documentation

- [ ] **API Docs**: Vérifier /api/docs/ accessible
- [ ] **README**: Mettre à jour avec infos production
- [ ] **Runbook**: Créer guide opérationnel
- [ ] **Contacts**: Documenter personnes à contacter

## Maintenance Continue

### Quotidien

- [ ] Vérifier logs erreurs
- [ ] Vérifier métriques (CPU, mémoire, DB)
- [ ] Vérifier uptime
- [ ] Vérifier backups réussis

### Hebdomadaire

- [ ] Analyser tendances utilisation
- [ ] Vérifier disk space
- [ ] Analyser logs sécurité
- [ ] Tester restauration backup

### Mensuel

- [ ] Mettre à jour dépendances
  ```bash
  pip list --outdated
  pip install -U package-name
  ```

- [ ] Scanner vulnérabilités
  ```bash
  safety check
  ```

- [ ] Revoir rate limits selon usage
- [ ] Optimiser queries lentes
- [ ] Nettoyer tokens expirés
  ```bash
  python manage.py flushexpiredtokens
  ```

### Trimestriel

- [ ] Audit sécurité complet
- [ ] Review architecture
- [ ] Test plan disaster recovery
- [ ] Formation équipe nouvelles features

## Rollback Plan

En cas de problème:

1. **Identifier** le problème via logs/monitoring
2. **Décider** si rollback nécessaire
3. **Rollback** vers version précédente:
   ```bash
   git checkout previous-stable-tag
   pip install -r requirements.txt
   python manage.py migrate
   sudo systemctl restart gunicorn
   ```
4. **Vérifier** système fonctionne
5. **Communiquer** avec équipe
6. **Post-mortem** analyser cause

## Contacts Urgence

- **DevOps Lead**:
- **DBA**:
- **Security**:
- **Product Owner**:

## Outils Recommandés

### Monitoring
- Sentry (erreurs)
- DataDog / New Relic (métriques)
- UptimeRobot (uptime)
- PagerDuty (alertes)

### CI/CD
- GitHub Actions
- GitLab CI
- Jenkins

### Backup
- AWS RDS Automated Backups
- pg_dump automatisé
- Redis RDB/AOF

### Load Balancing
- Nginx
- HAProxy
- AWS ELB/ALB

### Secrets Management
- AWS Secrets Manager
- HashiCorp Vault
- Azure Key Vault

## Ressources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)
- [12 Factor App](https://12factor.net/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Redis Security](https://redis.io/topics/security)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/security.html)

---

**Date de dernière révision**: 2026-01-02
**Version**: 1.0
**Responsable**: DevOps Team
