import json
from database import init_db, get_db_connection

def seed_data():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM representatives")
    if cursor.fetchone()[0] > 0:
        print("Database already populated.")
        return

    representatives = [
        {
            "name": "Amit Sharma",
            "role": "MP",
            "party": "Bharatiya Janata Party",
            "constituency": "New Delhi",
            "state": "Delhi",
            "image_url": "https://randomuser.me/api/portraits/men/32.jpg",
            "years_in_office": 4,
            "total_service_years": 9,
            "funds_allocated": 5.0,
            "funds_spent": 4.2,
            "achievements": json.dumps(["Improved Metro connectivity", "New public parks", "Skill development centers"]),
            "performance_rating": 4.5,
            "bio": "Amit Sharma has been vocal about urban infrastructure and sustainable development."
        },
        {
            "name": "Priya Singh",
            "role": "MLA",
            "party": "Aam Aadmi Party",
            "constituency": "Dwarka",
            "state": "Delhi",
            "image_url": "https://randomuser.me/api/portraits/women/44.jpg",
            "years_in_office": 2,
            "total_service_years": 2,
            "funds_allocated": 2.5,
            "funds_spent": 1.8,
            "achievements": json.dumps(["Mohalla Clinics expansion", "School renovation projects"]),
            "performance_rating": 4.2,
            "bio": "Priya Singh is a former teacher focused on education reform and healthcare accessibility."
        },
        {
            "name": "Rahul Verma",
            "role": "Councillor",
            "party": "Indian National Congress",
            "constituency": "Vasant Kunj",
            "state": "Delhi",
            "image_url": "https://randomuser.me/api/portraits/men/11.jpg",
            "years_in_office": 1,
            "total_service_years": 6,
            "funds_allocated": 1.0,
            "funds_spent": 0.9,
            "achievements": json.dumps(["Better waste management", "Street lighting improvements"]),
            "performance_rating": 3.8,
            "bio": "Rahul Verma has served in local governance for over 5 years, focusing on sanitation."
        },
         {
            "name": "S. Narayan",
            "role": "MP",
            "party": "DMK",
            "constituency": "Chennai South",
            "state": "Tamil Nadu",
            "image_url": "https://randomuser.me/api/portraits/men/55.jpg",
            "years_in_office": 3,
            "total_service_years": 15,
            "funds_allocated": 5.0,
            "funds_spent": 3.5,
            "achievements": json.dumps(["Tech park expansion", "Fishermen welfare schemes"]),
            "performance_rating": 4.7,
            "bio": "A veteran politician advocating for state rights and industrial growth."
        },
        {
            "name": "Anjali Desbmukh",
            "role": "MLA",
            "party": "Shiv Sena",
            "constituency": "Worli",
            "state": "Maharashtra",
            "image_url": "https://randomuser.me/api/portraits/women/68.jpg",
            "years_in_office": 4,
            "total_service_years": 4,
            "funds_allocated": 3.0,
            "funds_spent": 2.9,
            "achievements": json.dumps(["Coastal road project monitor", "Slum rehabilitation"]),
            "performance_rating": 4.6,
            "bio": "Young and dynamic leader focusing on urban redevelopment."
        }
    ]

    for rep in representatives:
        cursor.execute('''
        INSERT INTO representatives (name, role, party, constituency, state, image_url, years_in_office, total_service_years, funds_allocated, funds_spent, achievements, performance_rating, bio)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (rep['name'], rep['role'], rep['party'], rep['constituency'], rep['state'], rep['image_url'], rep['years_in_office'], rep['total_service_years'], rep['funds_allocated'], rep['funds_spent'], rep['achievements'], rep['performance_rating'], rep['bio']))

    conn.commit()
    conn.close()
    print("Seed data injected successfully.")

if __name__ == "__main__":
    seed_data()
