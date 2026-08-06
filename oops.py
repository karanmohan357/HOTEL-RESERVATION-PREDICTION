class Doctor:
    def __init__(self,doctor,speciality):
        self.doctor = doctor
        self.speciality = speciality

    def diagnose(doctor,speciality):
        print(f"Our main doctor is {doctor} and his speciality is {speciality}")
if __name__=="__main__":
    s1=Doctor("Sukumar","Ortho")
    print(s1.diagnose())