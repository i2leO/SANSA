import unittest
import hashlib
from datetime import date
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from app.auth import get_current_active_admin, get_current_user_optional, get_current_staff_or_admin
from app.models import Respondent, Visit, User, KnowledgePost, ScoringRuleValue
from test_sansa_result_integration import fixture

class ParticipantAccessTests(unittest.TestCase):
    def setUp(self):
        self.engine,self.db,_,self.visit,self.sansa,self.bia=fixture()
        KnowledgePost.__table__.create(self.engine)
        ScoringRuleValue.__table__.create(self.engine)
        self.other=Respondent(respondent_code='OTHER-SYNTHETIC',age=70,sex='female')
        self.db.add(self.other);self.db.flush()
        self.other_visit=Visit(respondent_id=self.other.id,visit_number=1,visit_date=date.today())
        self.db.add(self.other_visit);self.db.commit()
        self.admin=User(id=999,username='synthetic-admin',role='admin',is_active=True)
        app.dependency_overrides[get_db]=lambda:self.db
        app.dependency_overrides[get_current_active_admin]=lambda:self.admin
        self.client=TestClient(app)
    def tearDown(self):
        self.client.close();app.dependency_overrides.clear();self.db.close();self.engine.dispose()
    def issue(self):
        r=self.client.post(f'/participant-auth/respondents/{self.visit.respondent_id}/qr')
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.headers['cache-control'],'no-store')
        return r.json()['secret']
    def login(self,s):
        r=self.client.post('/participant-auth/login',json={'secret':s})
        self.assertEqual(r.status_code,200)
        return {'X-Respondent-Token':r.json()['access_token']}
    def test_random_hash_login_rotation(self):
        secret=self.issue();headers=self.login(secret)
        self.assertEqual(len(secret),43)
        self.assertEqual(self.visit.respondent.qr_secret_hash,hashlib.sha256(secret.encode()).hexdigest())
        own=f'/respondents/{self.visit.respondent.respondent_code}'
        self.assertEqual(self.client.get(own,headers=headers).status_code,200)
        self.assertNotIn('qr_secret_hash',self.client.get(own,headers=headers).json())
        self.assertNotEqual(secret,self.issue())
        self.assertEqual(self.client.post('/participant-auth/login',json={'secret':secret}).status_code,401)
        self.assertEqual(self.client.get(own,headers=headers).status_code,401)

    def test_staff_qr_login_and_rotation(self):
        staff = User(
            username='synthetic-staff', email='staff@example.test',
            hashed_password='not-used-in-qr-test', role='staff', is_active=True,
        )
        self.db.add(staff); self.db.commit()
        issued = self.client.post(f'/participant-auth/users/{staff.id}/qr')
        self.assertEqual(issued.status_code, 200)
        login = self.client.post('/participant-auth/login', json={'secret': issued.json()['secret']})
        self.assertEqual(login.status_code, 200)
        payload = login.json()
        self.assertEqual(payload['actor_type'], 'user')
        self.assertEqual(payload['user']['role'], 'staff')
        headers = {'Authorization': f"Bearer {payload['access_token']}"}
        self.assertEqual(self.client.get('/auth/me', headers=headers).status_code, 200)
        refreshed = self.client.post('/auth/refresh', json={'refresh_token': payload['refresh_token']})
        self.assertEqual(refreshed.status_code, 200)
        self.assertEqual(
            self.client.get('/auth/me', headers={'Authorization': f"Bearer {payload['refresh_token']}"}).status_code,
            401,
        )
        replacement = self.client.post(f'/participant-auth/users/{staff.id}/qr')
        self.assertEqual(replacement.status_code, 200)
        self.assertEqual(self.client.get('/auth/me', headers=headers).status_code, 401)
        self.assertEqual(self.client.post('/auth/refresh', json={'refresh_token': payload['refresh_token']}).status_code, 401)
    def test_cross_participant_and_anonymous_denied(self):
        headers=self.login(self.issue())
        paths=[f'/respondents/{self.other.respondent_code}',f'/visits/{self.other_visit.id}',f'/visits/respondent/{self.other.id}']+[f'/{kind}/visit/{self.other_visit.id}' for kind in ['sansa','bia','mna','satisfaction','food-diary']]
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code,401)
                self.assertEqual(self.client.get(path,headers=headers).status_code,403)
        self.assertEqual(self.client.get(f'/sansa/{self.sansa.id}',headers=headers).status_code,403)
        participant_result = self.client.post(
            f'/sansa/visit/{self.visit.id}/participant-result', headers=headers
        )
        self.assertEqual(participant_result.status_code, 200)
        self.assertEqual(set(participant_result.json()), {'predicted_group', 'ready', 'item_results'})
        self.assertEqual([item['number'] for item in participant_result.json()['item_results']], list(range(8, 17)))
        self.assertEqual(self.client.get(f'/bia/visit/{self.visit.id}',headers=headers).status_code,403)
        self.assertEqual(self.client.get(f'/mna/visit/{self.visit.id}',headers=headers).status_code,403)
        waist = self.client.put(
            f'/bia/visit/{self.visit.id}/waist',
            json={'waist_input_value': 91.5, 'waist_input_unit': 'cm', 'waist_circumference_cm': 91.5},
            headers=headers,
        )
        self.assertEqual(waist.status_code, 200)
        self.db.refresh(self.bia)
        self.assertEqual(float(self.bia.waist_circumference_cm), 91.5)
        inch = self.client.put(
            f'/bia/visit/{self.visit.id}/waist',
            json={'waist_input_value': 36, 'waist_input_unit': 'inch', 'waist_circumference_cm': 91.44},
            headers=headers,
        )
        self.assertEqual(inch.status_code, 200)
        self.db.refresh(self.bia)
        self.assertEqual(float(self.bia.waist_circumference_cm), 91.44)
        self.assertEqual(self.bia.waist_input_unit, 'inch')
        for path,body in [('/visits',{'respondent_id':self.other.id}),('/sansa',{'visit_id':self.other_visit.id}),('/respondents',{}),('/respondents/check-code',{'code':self.other.respondent_code})]:
            self.assertEqual(self.client.post(path,json=body,headers=headers).status_code,403)
    def test_issuer_auth_and_deleted_owner(self):
        app.dependency_overrides.pop(get_current_active_admin)
        self.assertIn(self.client.post(f'/participant-auth/respondents/{self.other.id}/qr').status_code,[401,403])
        app.dependency_overrides[get_current_active_admin]=lambda:self.admin
        secret=self.issue();headers=self.login(secret)
        self.visit.respondent.is_deleted=True;self.db.commit()
        self.assertEqual(self.client.post('/participant-auth/login',json={'secret':secret}).status_code,401)
        self.assertEqual(self.client.get(f'/visits/{self.visit.id}',headers=headers).status_code,401)
    def test_dashboard_and_pagination(self):
        app.dependency_overrides[get_current_staff_or_admin]=lambda:self.admin
        app.dependency_overrides[get_current_user_optional]=lambda:self.admin
        self.assertEqual(self.client.get('/admin/dashboard').json()['respondents'],2)
        first=self.client.get('/respondents?limit=1&skip=0');second=self.client.get('/respondents?limit=1&skip=1')
        self.assertEqual(first.headers['x-total-count'],'2')
        self.assertNotEqual(first.json()[0]['id'],second.json()[0]['id'])
        self.assertEqual(self.client.get('/respondents?limit=0').status_code,422)
        self.other.is_deleted=True;self.db.commit()
        self.assertEqual(self.client.get('/admin/dashboard').json()['respondents'],1)

    def test_scoring_versions_serialize_existing_relationship(self):
        app.dependency_overrides[get_current_staff_or_admin] = lambda: self.admin
        response = self.client.get('/scoring/versions')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]['rule_values'], [])

    def test_public_content_only_returns_visible_records(self):
        from app.models import Facility

        self.db.add_all([
            KnowledgePost(
                title='Published synthetic', slug='pub-test',
                content='Synthetic content', is_published=True,
            ),
            KnowledgePost(
                title='Draft synthetic', slug='draft-test',
                is_published=False,
            ),
            Facility(name='Active synthetic', is_active=True),
            Facility(name='Inactive synthetic', is_active=False),
        ])
        self.db.commit()

        posts = self.client.get('/knowledge').json()
        facilities = self.client.get('/facilities').json()
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0]['content'], 'Synthetic content')
        self.assertEqual(len(facilities), 1)
        self.assertEqual(facilities[0]['name'], 'Active synthetic')
        self.assertEqual(
            len(self.client.get('/knowledge?include_unpublished=true').json()), 1
        )
        self.assertEqual(
            len(self.client.get('/facilities?include_inactive=true').json()), 1
        )

    def test_malformed_ids_and_expired_sessions(self):
        from datetime import datetime, timedelta, timezone
        from jose import jwt
        from app.config import get_settings

        headers = self.login(self.issue())
        self.assertEqual(
            self.client.get('/sansa/not-an-id', headers=headers).status_code, 422
        )
        self.assertEqual(
            self.client.post(
                '/visits', json={'respondent_id': 'bad'}, headers=headers
            ).status_code,
            422,
        )
        settings = get_settings()
        expired = jwt.encode(
            {
                'sub': str(self.visit.respondent_id),
                'type': 'participant',
                'qr_version': self.visit.respondent.qr_secret_hash,
                'exp': datetime.now(timezone.utc) - timedelta(seconds=1),
            },
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        self.assertEqual(
            self.client.get(
                f'/visits/{self.visit.id}',
                headers={'X-Respondent-Token': expired},
            ).status_code,
            401,
        )
