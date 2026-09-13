import uuid
from app.database import SessionLocal
from app.models import HospitalGroup, Hospital, Facility, Department, HealthcareService

def seed_master_data():
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(HospitalGroup).first():
            print("Database already contains seed data. Skipping.")
            return

        # 1. Sunrise Healthcare Group (Tenant 1)
        sunrise_group = HospitalGroup(
            name="Sunrise Healthcare Group",
            code="SUNRISE"
        )
        db.add(sunrise_group)
        db.flush()

        # Hospital 1: Kanpur
        hosp_kanpur = Hospital(
            hospital_group_id=sunrise_group.id,
            name="Sunrise Hospital Kanpur",
            code="SH-KNP"
        )
        # Hospital 2: Lucknow
        hosp_lucknow = Hospital(
            hospital_group_id=sunrise_group.id,
            name="Sunrise Hospital Lucknow",
            code="SH-LKO"
        )
        db.add_all([hosp_kanpur, hosp_lucknow])
        db.flush()

        # Facility for Kanpur
        fac_kanpur = Facility(
            hospital_id=hosp_kanpur.id,
            name="Main Hospital Block"
        )
        db.add(fac_kanpur)
        db.flush()

        # Department
        dept_cardio = Department(
            facility_id=fac_kanpur.id,
            name="Cardiology"
        )
        db.add(dept_cardio)
        db.flush()

        # Healthcare Services
        srv_appt = HealthcareService(
            department_id=dept_cardio.id,
            name="Cardiology Outpatient Consultation",
            code="CARD-OPD"
        )
        srv_ref = HealthcareService(
            department_id=dept_cardio.id,
            name="Inpatient Cardiology Referral",
            code="CARD-REF"
        )
        db.add_all([srv_appt, srv_ref])

        # 2. Apollo Healthcare Group (Tenant 2 - for cross-tenant testing)
        apollo_group = HospitalGroup(
            name="Apollo Healthcare Group",
            code="APOLLO"
        )
        db.add(apollo_group)
        db.flush()

        hosp_delhi = Hospital(
            hospital_group_id=apollo_group.id,
            name="Apollo Hospital Delhi",
            code="AP-DEL"
        )
        db.add(hosp_delhi)

        db.commit()
        print("Seed data successfully inserted.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_master_data()
