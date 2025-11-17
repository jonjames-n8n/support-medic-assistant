#!/usr/bin/env python3
"""
Cloud Medic Assistant Tool
Interactive CLI for n8n Cloud Support operations
"""

import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


class CloudMedicTool:
    def __init__(self):
        self.workspace = None
        self.cluster = None
        self.pod_name = None
        self.downloads_dir = Path.home() / "Downloads"
        
    def print_header(self, text):
        """Print a formatted header"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{text.center(60)}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.END}\n")
    
    def print_success(self, text):
        """Print success message"""
        print(f"{Colors.GREEN}✓ {text}{Colors.END}")
    
    def print_error(self, text):
        """Print error message"""
        print(f"{Colors.RED}✗ {text}{Colors.END}")
    
    def print_info(self, text):
        """Print info message"""
        print(f"{Colors.BLUE}ℹ {text}{Colors.END}")
    
    def print_warning(self, text):
        """Print warning message"""
        print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")
    
    def run_command(self, cmd, capture_output=True, check=True):
        """Run a shell command and return output"""
        try:
            if capture_output:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    check=check
                )
                return result.stdout.strip() if result.stdout else None
            else:
                subprocess.run(cmd, shell=True, check=check)
                return None
        except subprocess.CalledProcessError as e:
            self.print_error(f"Command failed: {e}")
            if e.stderr:
                print(f"{Colors.RED}{e.stderr}{Colors.END}")
            return None
    
    def get_input(self, prompt, required=True):
        """Get user input with optional validation"""
        while True:
            value = input(f"{Colors.CYAN}{prompt}{Colors.END}").strip()
            if value or not required:
                return value
            self.print_error("This field is required. Please try again.")
    
    def confirm(self, message):
        """Ask for yes/no confirmation"""
        response = input(f"{Colors.YELLOW}{message} (y/n): {Colors.END}").strip().lower()
        return response in ['y', 'yes']
    
    def setup_workspace(self):
        """Get workspace name and cluster information"""
        self.print_header("Cloud Medic Assistant - Setup")
        
        self.workspace = self.get_input("Enter workspace name: ")
        self.cluster = self.get_input("Enter cluster (e.g., prod-users-gwc-48): ")
        
        # Switch to cluster
        self.print_info(f"Switching to cluster {self.cluster}...")
        result = self.run_command(f"kubectx {self.cluster}")
        if result is not None:
            self.print_success(f"Switched to cluster: {self.cluster}")
        else:
            self.print_error("Failed to switch cluster. Please verify cluster name.")
            return False
        
        # Get pod name
        self.print_info(f"Finding pod for workspace: {self.workspace}...")
        pod_cmd = f"kubectl get pods -n {self.workspace} -o jsonpath='{{.items[0].metadata.name}}'"
        self.pod_name = self.run_command(pod_cmd)
        
        if self.pod_name:
            self.print_success(f"Found pod: {self.pod_name}")
            return True
        else:
            self.print_error("Could not find pod. Please verify workspace name.")
            return False
    
    def show_main_menu(self):
        """Display main menu and get user choice"""
        self.print_header("Main Menu")
        print(f"{Colors.BOLD}Workspace:{Colors.END} {self.workspace}")
        print(f"{Colors.BOLD}Cluster:{Colors.END} {self.cluster}")
        print(f"{Colors.BOLD}Pod:{Colors.END} {self.pod_name}\n")
        
        menu_options = [
            ("1", "Export workflows (from live instance)", self.export_workflows),
            ("2", "Export workflows (from backup)", self.export_from_backup),
            ("3", "Import workflows", self.import_workflows),
            ("4", "Deactivate all workflows", self.deactivate_all_workflows),
            ("5", "Deactivate specific workflow", self.deactivate_workflow),
            ("6", "Check execution by ID", self.check_execution),
            ("7", "Cancel pending executions", self.cancel_pending_executions),
            ("8", "Cancel waiting executions", self.cancel_waiting_executions),
            ("9", "Take backup", self.take_backup),
            ("10", "View recent logs", self.view_logs),
            ("11", "Open database shell", self.open_database_shell),
            ("12", "Redeploy instance (cloudbot)", self.redeploy_instance),
            ("13", "Change workspace/cluster", self.setup_workspace),
            ("q", "Quit", None)
        ]
        
        for key, description, _ in menu_options:
            print(f"{Colors.GREEN}{key}.{Colors.END} {description}")
        
        print()
        choice = self.get_input("Select an option: ", required=False)
        
        # Find and execute the selected option
        for key, _, func in menu_options:
            if choice == key:
                if func:
                    func()
                return choice != 'q'
        
        self.print_error("Invalid option. Please try again.")
        return True
    
    def export_workflows(self):
        """Export workflows from live instance"""
        self.print_header("Export Workflows (Live Instance)")
        
        timestamp = datetime.now().strftime("%Y-%m-%d")
        filename = f"{self.workspace}-workflows-{timestamp}.json.gz"
        filepath = self.downloads_dir / filename
        
        self.print_info("Exporting workflows...")
        cmd = f"kubectl exec -it {self.pod_name} -n {self.workspace} -c n8n -- n8n export:workflow --pretty --all | gzip > {filepath}"
        
        result = self.run_command(cmd, capture_output=False)
        if result is not None or filepath.exists():
            self.print_success(f"Workflows exported to: {filepath}")
            self.print_info(f"Extract with: gzip -d {filename}")
        else:
            self.print_error("Export failed")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
    
    def export_from_backup(self):
        """Export workflows using workflow-exporter service"""
        self.print_header("Export Workflows (From Backup)")
        
        # Switch to services cluster
        self.print_info("Switching to services-gwc-1...")
        self.run_command("kubectx services-gwc-1")
        
        # List backups
        self.print_info("Listing available backups...")
        list_cmd = f"kubectl exec --context services-gwc-1 -n workflow-exporter -i deploy/workflow-exporter -- pnpm wf {self.workspace} list"
        print()
        self.run_command(list_cmd, capture_output=False)
        print()
        
        # Ask which backup to use
        backup_name = self.get_input("Enter backup name (or press Enter for latest): ", required=False)
        
        # Export
        self.print_info("Exporting workflows...")
        if backup_name:
            export_cmd = f"kubectl exec --context services-gwc-1 -n workflow-exporter -i deploy/workflow-exporter -- pnpm wf {self.workspace} export {backup_name}"
        else:
            export_cmd = f"kubectl exec --context services-gwc-1 -n workflow-exporter -i deploy/workflow-exporter -- pnpm wf {self.workspace} export"
        
        self.run_command(export_cmd, capture_output=False)
        
        # Download
        self.print_info("Downloading archive...")
        timestamp = datetime.now().strftime("%Y-%m-%d")
        filename = f"{self.workspace}-workflows-backup-{timestamp}.zip"
        filepath = self.downloads_dir / filename
        
        download_cmd = f"kubectl exec --context services-gwc-1 -n workflow-exporter -i deploy/workflow-exporter -- cat /tmp/output/{self.workspace}-workflows.zip > {filepath}"
        result = self.run_command(download_cmd, capture_output=False)
        
        if filepath.exists():
            self.print_success(f"Workflows downloaded to: {filepath}")
        else:
            self.print_error("Download failed")
        
        # Switch back to original cluster
        self.run_command(f"kubectx {self.cluster}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
    
    def import_workflows(self):
        """Import workflows to instance"""
        self.print_header("Import Workflows")
        
        # Ask for file path
        self.print_info("Available files in Downloads:")
        json_files = list(self.downloads_dir.glob("*.json"))
        
        if not json_files:
            self.print_error("No .json files found in Downloads folder")
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
            return
        
        for idx, file in enumerate(json_files, 1):
            print(f"{idx}. {file.name}")
        
        print()
        choice = self.get_input("Select file number (or enter full path): ")
        
        try:
            file_idx = int(choice) - 1
            if 0 <= file_idx < len(json_files):
                local_file = json_files[file_idx]
            else:
                self.print_error("Invalid selection")
                input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
                return
        except ValueError:
            local_file = Path(choice)
            if not local_file.exists():
                self.print_error("File not found")
                input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
                return
        
        # Confirm
        if not self.confirm(f"Import {local_file.name}?"):
            self.print_info("Import cancelled")
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
            return
        
        # Copy to pod
        self.print_info("Copying file to pod...")
        remote_path = f"/home/node/{local_file.name}"
        copy_cmd = f"kubectl cp {local_file} {self.workspace}/{self.pod_name}:{remote_path} -c n8n"
        self.run_command(copy_cmd, capture_output=False)
        
        # Import
        self.print_info("Importing workflows...")
        import_cmd = f"kubectl exec -it {self.pod_name} -n {self.workspace} -c n8n -- n8n import:workflow --input={remote_path}"
        self.run_command(import_cmd, capture_output=False)
        
        self.print_success("Import complete!")
        self.print_warning("Remember: Imported workflows are deactivated by default")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
    
    def deactivate_all_workflows(self):
        """Deactivate all workflows in database"""
        self.print_header("Deactivate All Workflows")
        
        self.print_warning("This will deactivate ALL active workflows!")
        if not self.confirm("Are you sure?"):
            self.print_info("Operation cancelled")
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
            return
        
        self.print_info("Taking backup first...")
        backup_cmd = f"kubectl exec -it {self.pod_name} -n {self.workspace} -c backup-cron -- n8n-backup.py backup"
        self.run_command(backup_cmd, capture_output=False)
        
        self.print_info("Deactivating workflows...")
        sql_cmd = "UPDATE workflow_entity SET active = 0 WHERE active = 1;"
        db_cmd = f"kubectl exec -it {self.pod_name} -n {self.workspace} -c backup-cron -- sqlite3 database.sqlite \"{sql_cmd}\""
        
        result = self.run_command(db_cmd)
        if result is not None:
            self.print_success("All workflows deactivated")
            self.print_warning("Redeploy instance for changes to take effect")
        else:
            self.print_error("Failed to deactivate workflows")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
    
    def deactivate_workflow(self):
        """Deactivate specific workflow by ID"""
        self.print_header("Deactivate Specific Workflow")
        
        workflow_id = self.get_input("Enter workflow ID: ")
        
        if not self.confirm(f"Deactivate workflow {workflow_id}?"):
            self.print_info("Operation cancelled")
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
            return
        
        self.print_info("Taking backup first...")
        backup_cmd = f"kubectl exec -it {self.pod_name} -n {self.workspace} -c backup-cron -- n8n-backup.py backup"
        self.run_command(backup_cmd, capture_output=False)
        
        self.print_info("Deactivating workflow...")
        sql_cmd = f"UPDATE workflow_entity SET active = 0 WHERE id = '{workflow_id}';"
        db_cmd = f"kubectl exec -it {self.pod_name} -n {self.workspace} -c backup-cron -- sqlite3 database.sqlite \"{sql_cmd}\""
        
        result = self.run_command(db_cmd)
        if result is not None:
            self.print_success(f"Workflow {workflow_id} deactivated")
            self.print_warning("Redeploy instance for changes to take effect")
        else:
            self.print_error("Failed to deactivate workflow")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
    
    def check_execution(self):
        """Check execution details by ID"""
        self.print_header("Check Execution")
        
        execution_id = self.get_input("Enter execution ID: ")
        
        self.print_info("Fetching execution details...")
        sql_cmd = f"SELECT id, workflowId, finished, mode, startedAt, stoppedAt, status FROM execution_entity WHERE id = {execution_id};"
        db_cmd = f"kubectl exec -it {self.pod_name} -n {self.workspace} -c backup-cron -- sqlite3 database.sqlite \"{sql_cmd}\""
        
        print(f"\n{Colors.BOLD}Execution Summary:{Colors.END}")
        self.run_command(db_cmd, capture_output=False)
        
        if self.confirm("\nView execution data (error details)?"):
            sql_cmd = f"SELECT data FROM execution_data WHERE executionId = '{execution_id}';"
            db_cmd = f"kubectl exec -it {self.pod_name} -n {self.workspace} -c backup-cron -- sqlite3 database.sqlite \"{sql_cmd}\""
            print()
            self.run_command(db_cmd, capture_output=False)
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
    
    def cancel_pending_executions(self):
        """Cancel pending executions"""
        self.print_header("Cancel Pending Executions")
        
        # Count pending
        count_cmd = f"kubectl exec -it {self.pod_name} -n {self.workspace} -c backup-cron -- sqlite3 database.sqlite \"SELECT COUNT(*) FROM execution_entity WHERE status = 'new';\""
        count = self.run_command(count_cmd)
        
        self.print_info(f"Pending executions: {count}")
        
        if not count or count == "0":
            self.print_info("No pending executions to cancel")
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
            return
        
        if not self.confirm(f"Cancel {count} pending executions?"):
            self.print_info("Operation cancelled")
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
            return
        
        self.print_info("Cancelling pending executions...")
        sql_cmd = "UPDATE execution_entity SET status = 'crashed' WHERE status = 'new';"
        db_cmd = f"kubectl exec -it {self.pod_name} -n {self.workspace} -c backup-cron -- sqlite3 database.sqlite \"{sql_cmd}\""
        
        self.run_command(db_cmd)
        self.print_success(f"Cancelled {count} pending executions")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
    
    def cancel_waiting_executions(self):
        """Cancel waiting executions"""
        self.print_header("Cancel Waiting Executions")
        
        # Count waiting
        count_cmd = f"kubectl exec -it {self.pod_name} -n {self.workspace} -c backup-cron -- sqlite3 database.sqlite \"SELECT COUNT(*) FROM execution_entity WHERE status = 'waiting';\""
        count = self.run_command(count_cmd)
        
        self.print_info(f"Waiting executions: {count}")
        
        if not count or count == "0":
            self.print_info("No waiting executions to cancel")
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
            return
        
        if not self.confirm(f"Cancel {count} waiting executions?"):
            self.print_info("Operation cancelled")
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
            return
        
        self.print_info("Cancelling waiting executions...")
        sql_cmd = "UPDATE execution_entity SET status = 'crashed' WHERE status = 'waiting';"
        db_cmd = f"kubectl exec -it {self.pod_name} -n {self.workspace} -c backup-cron -- sqlite3 database.sqlite \"{sql_cmd}\""
        
        self.run_command(db_cmd)
        self.print_success(f"Cancelled {count} waiting executions")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
    
    def take_backup(self):
        """Take manual backup"""
        self.print_header("Take Backup")
        
        self.print_info("Creating backup...")
        backup_cmd = f"kubectl exec -it {self.pod_name} -n {self.workspace} -c backup-cron -- n8n-backup.py backup"
        self.run_command(backup_cmd, capture_output=False)
        
        self.print_success("Backup complete!")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
    
    def view_logs(self):
        """View recent logs"""
        self.print_header("View Recent Logs")
        
        lines = self.get_input("Number of lines (default 50): ", required=False) or "50"
        
        self.print_info(f"Fetching last {lines} lines...")
        log_cmd = f"kubectl logs {self.pod_name} -n {self.workspace} -c n8n --tail={lines}"
        print()
        self.run_command(log_cmd, capture_output=False)
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
    
    def open_database_shell(self):
        """Open interactive database shell"""
        self.print_header("Database Shell")
        
        self.print_info("Opening SQLite shell...")
        self.print_warning("Type .quit to exit")
        print()
        
        db_cmd = f"kubectl exec -it {self.pod_name} -n {self.workspace} -c backup-cron -- sqlite3 database.sqlite"
        os.system(db_cmd)
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
    
    def redeploy_instance(self):
        """Redeploy instance using cloudbot"""
        self.print_header("Redeploy Instance")
        
        self.print_warning("This will restart the instance")
        if not self.confirm("Proceed with redeploy?"):
            self.print_info("Redeploy cancelled")
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
            return
        
        self.print_info("Redeploying instance...")
        redeploy_cmd = f"/cloudbot redeploy-instance {self.workspace}"
        
        # This needs to be run in Slack, so just show the command
        print(f"\n{Colors.YELLOW}Run this command in Slack:{Colors.END}")
        print(f"{Colors.BOLD}{redeploy_cmd}{Colors.END}\n")
        
        input(f"{Colors.CYAN}Press Enter to continue...{Colors.END}")
    
    def run(self):
        """Main application loop"""
        try:
            # Setup
            if not self.setup_workspace():
                return
            
            # Main loop
            while True:
                if not self.show_main_menu():
                    break
            
            self.print_header("Goodbye!")
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}Interrupted by user{Colors.END}")
            sys.exit(0)
        except Exception as e:
            self.print_error(f"Unexpected error: {e}")
            sys.exit(1)


def main():
    """Entry point"""
    tool = CloudMedicTool()
    tool.run()


if __name__ == "__main__":
    main()
