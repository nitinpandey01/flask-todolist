from flask import url_for
from flask_testing import TestCase

from app import create_app, db
from app.models import User


class TodolistClientTestCase(TestCase):
    def create_app(self):
        return create_app("testing")

    def setUp(self):
        db.create_all()
        self.username_alice = "alice"

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def register_user(self, name):
        response = self.client.post(
            url_for("auth.register"),
            data={
                "username": name,
                "email": name + "@example.com",
                "password": "correcthorsebatterystaple",
                "password_confirmation": "correcthorsebatterystaple",
            },
        )
        return response

    def login_user(self, name):
        response = self.client.post(
            url_for("auth.login"),
            data={
                "email_or_username": name + "@example.com",
                "password": "correcthorsebatterystaple",
            },
        )
        return response

    def register_and_login(self, name):
        response = self.register_user(name)
        self.assert_redirects(response, "/auth/login")
        response = self.login_user(name)
        self.assert_redirects(response, "/")

    def test_home_page(self):
        response = self.client.get(url_for("main.index"))
        self.assert_200(response)
        self.assert_template_used("index.html")

    def test_register_page(self):
        response = self.client.get(url_for("auth.register"))
        self.assert_200(response)
        self.assert_template_used("register.html")

    def test_login_page(self):
        response = self.client.get(url_for("auth.login"))
        self.assert_200(response)
        self.assert_template_used("login.html")

    def test_last_seen_update_after_login(self):
        self.register_user(self.username_alice)
        user = User.query.filter_by(username=self.username_alice).first()
        before = user.last_seen
        self.login_user(self.username_alice)
        after = user.last_seen
        self.assertNotEqual(before, after)
