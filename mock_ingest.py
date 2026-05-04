from faker import Faker
def main():
    fake = Faker()
    for _ in range(10):
        print(fake.name())
if __name__ == "__main__":
    main()
