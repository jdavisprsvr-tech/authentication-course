from app import create_app

app = create_app("testing")

with app.test_client() as client:

    # 1) register
    register_resp = client.post("/register", json={
        # expected fields
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "TestPassword123!"
    })
    print("Register status:", register_resp.status_code)
    print("Register body:", register_resp.get_json())

    # 2) login
    login_resp = client.post("/login", json={
        # matching credentials
        "username": "testuser",
        "password": "TestPassword123!"
    })
    print("Login status:", login_resp.status_code)
    print("Login body:", login_resp.get_json())
    
    # 3) Get recipes
    login_data = login_resp.get_json()
    token = login_data.get("token") if login_data else None

    if token:
        response = client.get(
            "/recipes",
            headers={"Authorization": f"Bearer {token}"}
        )
        print("Recipes status:", response.status_code)
        print("Recipes body:", response.get_json())
    else:
        print("Login failed; cannot test recipes.")