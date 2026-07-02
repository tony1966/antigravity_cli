import argparse
import sys
from datetime import datetime
from todo.storage import Storage
from todo.manager import TodoManager

def parse_iso_datetime(iso_str: str) -> str:
    """Parses an ISO format datetime string and returns a user-friendly format."""
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return iso_str

def handle_add(manager: TodoManager, args):
    if not args.title or not args.title.strip():
        print("Error: Todo title cannot be empty.")
        sys.exit(1)
    
    new_todo = manager.add(args.title)
    print(f"Added task: [ID: {new_todo['id']}] \"{new_todo['title']}\"")

def handle_list(manager: TodoManager, args):
    # Determine filter status
    if args.done:
        status = "done"
    elif args.pending:
        status = "pending"
    else:
        status = "all"
        
    todos = manager.list_todos(status)
    if not todos:
        print(f"No {status if status != 'all' else ''} tasks found.")
        return

    print(f"{'ID':<4} {'Status':<8} {'Title':<40} {'Created At':<16}")
    print("-" * 72)
    for todo in todos:
        status_str = "[x]" if todo["done"] else "[ ]"
        created_time = parse_iso_datetime(todo["created_at"])
        print(f"{todo['id']:<4} {status_str:<8} {todo['title']:<40} {created_time:<16}")

def handle_done(manager: TodoManager, args):
    success = manager.mark_done(args.id)
    if success:
        print(f"Success: Marked task {args.id} as completed.")
    else:
        print(f"Error: Task with ID {args.id} not found.")
        sys.exit(1)

def handle_delete(manager: TodoManager, args):
    success = manager.delete(args.id)
    if success:
        print(f"Success: Deleted task {args.id}.")
    else:
        print(f"Error: Task with ID {args.id} not found.")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Todo CLI Application - Manage your tasks from the terminal."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # 'add' subcommand
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("title", type=str, help="The title of the task")

    # 'list' subcommand
    list_parser = subparsers.add_parser("list", help="List tasks")
    group = list_parser.add_mutually_exclusive_group()
    group.add_argument("--done", action="store_true", help="List only completed tasks")
    group.add_argument("--pending", action="store_true", help="List only pending tasks")
    group.add_argument("--all", action="store_true", default=True, help="List all tasks (default)")

    # 'done' subcommand
    done_parser = subparsers.add_parser("done", help="Mark a task as completed")
    done_parser.add_argument("id", type=int, help="ID of the task to mark as done")

    # 'delete' subcommand
    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("id", type=int, help="ID of the task to delete")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Initialize storage and manager
    storage = Storage("todo_data.json")
    manager = TodoManager(storage)

    # Dispatch to handlers
    if args.command == "add":
        handle_add(manager, args)
    elif args.command == "list":
        handle_list(manager, args)
    elif args.command == "done":
        handle_done(manager, args)
    elif args.command == "delete":
        handle_delete(manager, args)

if __name__ == "__main__":
    main()
