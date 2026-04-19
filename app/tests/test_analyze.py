from fastapi.testclient import TestClient

from app.main import app



client = TestClient(app)





def test_health():

    response = client.get("/")

    assert response.status_code == 200





def test_analyze_resume():



    payload = {

        "text": "Software engineer with experience in ASP.NET Core, SQL, and APIs."

    }



    response = client.post("/analyze/text", json=payload)



    assert response.status_code == 200



    data = response.json()



    assert "summary" in data

    assert "atsScore" in data

    assert isinstance(data["strengths"], list)

    assert isinstance(data["weaknesses"], list)

