import os
import sys

# Add src folder to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("=" * 55)
    print(" VACCINATION SCHEDULING AND COLD-CHAIN ENGINE")
    print("=" * 55)

    print("\nSystem Started Successfully!")

    print("\nAvailable Modules:")
    print("1. Beneficiary Management")
    print("2. Dose Management")
    print("3. Vaccination Scheduling")
    print("4. Inventory Management")
    print("5. Cold-Chain Monitoring")
    print("6. AEFI Management")
    print("7. Reports")
    print("8. Exit")

    choice = input("\nEnter your choice (1-8): ")

    if choice == "1":
        print("Beneficiary Management Selected")
    elif choice == "2":
        print("Dose Management Selected")
    elif choice == "3":
        print("Vaccination Scheduling Selected")
    elif choice == "4":
        print("Inventory Management Selected")
    elif choice == "5":
        print("Cold-Chain Monitoring Selected")
    elif choice == "6":
        print("AEFI Management Selected")
    elif choice == "7":
        print("Reports Selected")
    elif choice == "8":
        print("Exiting System...")
    else:
        print("Invalid Choice!")

if __name__ == "__main__":
    main()