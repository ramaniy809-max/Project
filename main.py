import os
from datetime import datetime, timedelta
from login import LoginManager

def main():
    manager = LoginManager()
    
    while True:
        print("\n--- Personal Finance Book ---")
        print("1. Login to Account")
        print("2. Register New Account")
        print("3. Exit")
        
        try:
            choice = int(input("Enter your choice: "))
        except ValueError:
            print("Enter a valid number.")
            continue

        if choice == 1:
            if manager.authenticate_user():
                username = manager.current_user
                print(f"\nWelcome, {username}! Opening your secure workspace...")
                
                # Set dynamic path for the logged-in user
                user_dir = os.path.join("users", username)
                os.makedirs(user_dir, exist_ok=True)
                transaction_file = os.path.join(user_dir, "transactions.txt")
                
                run_app(transaction_file, username)
        elif choice == 2:
            manager.register_user()
        elif choice == 3:
            print("Exiting application...")
            break
        else:
            print("Choose a number from 1 to 3.")

# Main application loop for transaction management
def run_app(transaction_file, username):
    while True:
        print(f"\n--- Transaction Menu ({username}) ---")
        print("1. Enter your transaction")
        print("2. See your transactions")
        print("3. Calculate all transactions (Net Balance)")
        print("4. Delete transactions")
        print("5. Logout")
        
        try:
            ch = int(input("Enter your choice: "))
        except ValueError:
            print("Invalid input! Please enter a correct number.")
            continue  

        if ch == 1:
            enter_transaction(transaction_file)
        elif ch == 2:
            see_transaction(transaction_file)
        elif ch == 3:
            calculate_transaction(transaction_file)
        elif ch == 4:
            delete_transaction(transaction_file)
        elif ch == 5:
            print("Logging out...")
            break
        else:
            print("Invalid choice. Please choose between 1 and 5.")

# Function to enter a credit or debit transaction using a while loop
def enter_transaction(transaction_file):
    while True:
        print("\n--- Enter Transaction Menu ---")
        print("1. Credit")
        print("2. Debit")
        print("3. Back to Menu")
        
        try:
            choice = int(input("Enter your choice: "))
            if choice == 3:
                break
            
            if choice not in [1, 2]:
                print("Enter correct number (1, 2, or 3)")
                continue

            trans_type = "Credit" if choice == 1 else "Debit"
            amount = float(input(f"Enter {trans_type} amount: "))
            
            if amount <= 0:
                print("Amount must be greater than zero.")
                continue

            description = input("Enter description: ").strip()
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            # Save transaction to user-specific file
            with open(transaction_file, "a", encoding="utf-8") as f:
                f.write(f"{trans_type},{amount},{description},{current_date}\n")
            print(f"Success: {trans_type} of {amount} recorded on {current_date}!")
            
        except ValueError:
            print("Enter correct value / number.")

# Function to view all stored transactions using a while loop
def see_transaction(transaction_file):
    while True:
        print("\n--- See Transactions Menu ---")
        print("1. View All Transactions")
        print("2. Back to Menu")
        
        try:
            choice = int(input("Enter your choice: "))
            if choice == 2:
                break
            elif choice == 1:
                if not os.path.exists(transaction_file):
                    print("No transactions found.")
                    continue
                
                with open(transaction_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    if not lines:
                        print("No transactions found.")
                        continue
                    print(f"\n{'Type':<10} | {'Amount':<10} | {'Description':<15} | {'Date'}")
                    print("-" * 55)
                    for line in lines:
                        parts = line.strip().split(",")
                        if len(parts) >= 4:
                            t_type, amount, desc, date_str = parts[0], parts[1], parts[2], parts[3]
                            print(f"{t_type:<10} | {amount:<10} | {desc:<15} | {date_str}")
                        elif len(parts) == 3:
                            t_type, amount, desc = parts
                            print(f"{t_type:<10} | {amount:<10} | {desc:<15} | N/A")
            else:
                print("Enter correct number (1 or 2)")
        except ValueError:
            print("Enter correct number.")

# Function to calculate transactions using a while loop
def calculate_transaction(transaction_file):
    while True:
        print("\n--- Calculate Transactions Menu ---")
        print("1. Calculate Net Balance (All Time)")
        print("2. Calculate Specific Timeline Data")
        print("3. Back to Menu")
        
        try:
            choice = int(input("Enter your choice: "))
            if choice == 3:
                break
            
            if not os.path.exists(transaction_file):
                print("No transactions found.")
                continue

            if choice == 1:
                total_credit = 0.0
                total_debit = 0.0

                with open(transaction_file, "r", encoding="utf-8") as f:
                    for line in f:
                        parts = line.strip().split(",")
                        if len(parts) >= 3:
                            t_type, amount = parts[0], parts[1]
                            if t_type == "Credit":
                                total_credit += float(amount)
                            elif t_type == "Debit":
                                total_debit += float(amount)
                
                net_balance = total_credit - total_debit
                print(f"\n--- All-Time Summary ---")
                print(f"Total Credit: {total_credit}")
                print(f"Total Debit:  {total_debit}")
                print(f"Net Balance:  {net_balance}")

            elif choice == 2:
                print("-" * 25)
                print("W = Weekly transactions (Last 7 days)")
                print("M = Monthly transactions (Current month)")
                print("Y = Yearly transactions (Current year)")
                print("-" * 25)
                
                time_choice = input("Enter your choice (W/M/Y): ").strip().lower()
                
                if time_choice not in ['w', 'm', 'y']:
                    print("Invalid choice. Please enter W, M, or Y.")
                    continue

                today = datetime.now()
                total_credit = 0.0
                total_debit = 0.0

                with open(transaction_file, "r", encoding="utf-8") as f:
                    for line in f:
                        parts = line.strip().split(",")
                        if len(parts) >= 4:  
                            t_type, amount, _, date_str = parts[0], parts[1], parts[2], parts[3]
                            try:
                                trans_date = datetime.strptime(date_str, "%Y-%m-%d")
                            except ValueError:
                                continue

                            if time_choice == 'w' and (today - trans_date) <= timedelta(days=7):
                                if t_type == "Credit": total_credit += float(amount)
                                else: total_debit += float(amount)
                            elif time_choice == 'm' and trans_date.year == today.year and trans_date.month == today.month:
                                if t_type == "Credit": total_credit += float(amount)
                                else: total_debit += float(amount)
                            elif time_choice == 'y' and trans_date.year == today.year:
                                if t_type == "Credit": total_credit += float(amount)
                                else: total_debit += float(amount)

                period_name = {"w": "Weekly", "m": "Monthly", "y": "Yearly"}[time_choice]
                net_balance = total_credit - total_debit
                
                print(f"\n--- {period_name} Summary ---")
                print(f"Total Credit: {total_credit}")
                print(f"Total Debit:  {total_debit}")
                print(f"Net Balance:  {net_balance}")

            else:
                print("Enter correct number (1, 2, or 3)")

        except ValueError:
            print("Invalid input. Please enter a correct number.")

def delete_transaction(transaction_file):
    while True:
        print("\n--- Delete Transactions Menu ---")
        print("1. Clear All Transactions")
        print("2. Delete Specific Timeline Data")
        print("3. Back to Menu")
        
        try:
            choice = int(input("Enter your choice: "))
            if choice == 3:
                break
            
            if not os.path.exists(transaction_file):
                print("No transactions found.")
                continue

            if choice == 1:
                confirm = input("Are you sure you want to delete ALL transactions? (y/n): ").strip().lower()
                if confirm == 'y':
                    open(transaction_file, "w", encoding="utf-8").close()
                    print("All transactions deleted successfully.")

            elif choice == 2:
                print("-" * 30)
                print("W = Delete weekly transactions (Last 7 days)")
                print("M = Delete monthly transactions (Current month)")
                print("Y = Delete yearly transactions (Current year)")
                print("-" * 30)
                
                time_choice = input("Enter your choice (W/M/Y): ").strip().lower()
                
                if time_choice not in ['w', 'm', 'y']:
                    print("Invalid choice. Please enter W, M, or Y.")
                    continue
                
                period_name = {"w": "Weekly", "m": "Monthly", "y": "Yearly"}[time_choice]
                confirm = input(f"Are you sure you want to delete all {period_name} transactions? (y/n): ").strip().lower()
                if confirm != 'y':
                    print("Deletion cancelled.")
                    continue

                today = datetime.now()
                remaining_lines = []
                deleted_count = 0

                with open(transaction_file, "r", encoding="utf-8") as f:
                    for line in f:
                        parts = line.strip().split(",")
                        if len(parts) >= 4:  
                            _, _, _, date_str = parts[0], parts[1], parts[2], parts[3]
                            try:
                                trans_date = datetime.strptime(date_str, "%Y-%m-%d")
                            except ValueError:
                                remaining_lines.append(line)
                                continue

                            is_match = False
                            if time_choice == 'w' and (today - trans_date) <= timedelta(days=7):
                                is_match = True
                            elif time_choice == 'm' and trans_date.year == today.year and trans_date.month == today.month:
                                is_match = True
                            elif time_choice == 'y' and trans_date.year == today.year:
                                is_match = True

                            if is_match:
                                deleted_count += 1
                            else:
                                remaining_lines.append(line)
                        else:
                            remaining_lines.append(line)

                with open(transaction_file, "w", encoding="utf-8") as f:
                    f.writelines(remaining_lines)

                print(f"Success: Deleted {deleted_count} {period_name} transaction(s).")

            else:
                print("Enter correct number (1, 2, or 3)")

        except ValueError:
            print("Invalid input. Please enter a correct number.")

if __name__ == "__main__":
    main()