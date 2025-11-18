#!/usr/bin/env python3
"""
Cloud Medic Assistant Tool v1.1
Interactive CLI for n8n Cloud Support operations

Changelog v1.1:
- Added VPN connection reminder
- Simplified cluster input (just number, e.g., "48")
- Added guided DB troubleshooting menu with pre-built queries
- Better error handling for database queries
- Health check feature (option 0)
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
        self.cluster_number = None
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
    
    def run_db_query(self, sql_cmd, show_error_details=True):
        """Run database query with better error handling"""
        try:
            db_cmd = f"kubectl exec -it {self.pod_name} -n {self.workspace} -c backup-cron -- sqlite3 database.sqlite \"{sql_cmd}\""
            result = self.run_command(db_cmd, capture_output=True, check=True)
            return result
        except Exception as e:
            self.print_error("Database query failed - connection issue or data too large")
            if show_error_details:
                self.print_info("Possible causes:")
                print("  • Network/VPN connection interrupted")
                print("  • Pod restarted during query")
                print("  • Data size too large to transfer")
                print("  • Execution ID doesn't exist")
            if self.confirm("\nRetry query?"):
                return self.run_db_query(sql_cmd, show_error_details=False)
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
        self.print_header("Cloud Medic Assistant - Setup v1.1")
        
        # VPN reminder
        self.print_warning("REMINDER: Make sure you're connected to the VPN!")
        print()
        
        self.workspace = self.get_input("Enter workspace name: ")
        
        # Simplified cluster input
        cluster_input = self.get_input("Enter cluster number (e.g., 48 for prod-users-gwc-48): ")
        self.cluster_number = cluster_input
        self.cluster = f"prod-users-gwc-{cluster_input}"
        
        # Switch to cluster
        self.print_info(f"Switching to cluster {self.cluster}...")
        result = self.run_command(f"kubectx {self.cluster}")
        if result is not None:
            self.print_success(f"Switched to cluster: {self.cluster}")
        else:
            self.print_error("Failed to switch cluster. Please verify cluster number.")
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
            ("0", "Health check (quick status)", self.health_check),
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
            ("11", "Database troubleshooting (guided)", self.database_troubleshooting),
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
    
    def health_check(self):
        """Quick health check of pod and database"""
        self.print_header("Health Check")
        
        # Pod status
        self.print_info("Checking pod status...")
        pod_status_cmd = f"kubectl get pod {self.pod_name} -n {self.workspace} -o jsonpath='{{.status.phase}} {{.status.containerStatuses[*].ready}} {{.status.containerStatuses[*].restartCount}} {{.metadata.creationTimestamp}}'"
        pod_status = self.run_command(pod_status_cmd)
        
        if pod_status:
            parts = pod_status.split()
            phase = parts[0] if len(parts) > 0 else "Unknown"
            ready = parts[1] if len(parts) > 1 else "Unknown"
            restarts = parts[2] if len(parts) > 2 else "0"
            created = parts[3] if len(parts) > 3 else "Unknown"
            
            print(f"\n{Colors.BOLD}Pod Status:{Colors.END}")
            
            # Phase status
            if phase == "Running":
                print(f"  Status: {Colors.GREEN}✓ {phase}{Colors.END}")
            else:
                print(f"  Status: {Colors.RED}✗ {phase}{Colors.END}")
            
            # Container ready status
            if "true" in ready.lower():
                print(f"  Containers: {Colors.GREEN}✓ Ready{Colors.END}")
            else:
                print(f"  Containers: {Colors.YELLOW}⚠ Not all ready{Colors.END}")
            
            # Restart count - handle multiple containers
            try:
                restart_counts = [int(r) for r in restarts.split() if r.isdigit()]
                restart_count = max(restart_counts) if restart_counts else 0
            except (ValueError, AttributeError):
                restart_count = 0
            
            if restart_count == 0:
                print(f"  Restarts: {Colors.GREEN}✓ 0{Colors.END}")
            elif restart_count < 5:
                print(f"  Restarts: {Colors.YELLOW}⚠ {restart_count}{Colors.END}")
            else:
                print(f"  Restarts: {Colors.RED}✗ {restart_count} (Check logs!){Colors.END}")
            
            print(f"  Age: {created}")
        
        # Database size
        self.print_info("\nChecking database size...")
        size_cmd = f"kubectl exec -it {self.pod_name} -n {self.workspace} -c backup-cron -- du -sh database.sqlite 2>/dev/null | awk '{{print $1}}'"
        db_size = self.run_command(size_cmd)
        if db_size:
            print(f"{Colors.BOLD}Database Size:{Colors.END} {db_size}")
        
        # Active workflows count
        sql_cmd = "SELECT COUNT(*) FROM workflow_entity WHERE active = 1;"
        active_wf = self.run_db_query(sql_cmd, show_error_details=False)
        if active_wf:
            print(f"{Colors.BOLD}Active Workflows:{Colors.END} {active_wf}")
        
        # Total executions
        sql_cmd = "SELECT COUNT(*) FROM execution_entity;"
        total_exec = self.run_db_query(sql_cmd, show_error_details=False)
        if total_exec:
            print(f"{Colors.BOLD}Total Executions:{Colors.END} {total_exec}")
        
        # Recent errors (last 24h)
        self.print_info("\nChecking recent errors (last 24h)...")
        sql_cmd = "SELECT COUNT(*) FROM execution_entity WHERE status IN ('error', 'crashed', 'failed') AND datetime(startedAt) > datetime('now', '-1 day');"
        recent_errors = self.run_db_query(sql_cmd, show_error_details=False)
        
        if recent_errors:
            error_count = int(recent_errors)
            if error_count == 0:
                print(f"{Colors.BOLD}Recent Errors:{Colors.END} {Colors.GREEN}✓ 0{Colors.END}")
            elif error_count < 10:
                print(f"{Colors.BOLD}Recent Errors:{Colors.END} {Colors.YELLOW}⚠ {error_count}{Colors.END}")
            else:
                print(f"{Colors.BOLD}Recent Errors:{Colors.END} {Colors.RED}✗ {error_count} (Investigate!){Colors.END}")
        
        # Overall health summary
        print(f"\n{Colors.BOLD}Overall Health:{Colors.END}")
        if pod_status and phase == "Running" and restart_count < 5 and (not recent_errors or int(recent_errors) < 10):
            print(f"{Colors.GREEN}✓ Healthy{Colors.END}")
        elif pod_status and phase == "Running":
            print(f"{Colors.YELLOW}⚠ Running with issues - review above{Colors.END}")
        else:
            print(f"{Colors.RED}✗ Unhealthy - needs attention{Colors.END}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
    
    def database_troubleshooting(self):
        """Show database troubleshooting menu"""
        while True:
            self.print_header("Database Troubleshooting")
            
            troubleshooting_options = [
                ("1", "Check crashloop causes", self.check_crashloop_causes),
                ("2", "View workflow history", self.view_workflow_history),
                ("3", "List all workflows", self.list_workflows),
                ("4", "View recent errors", self.view_recent_errors),
                ("5", "Check database info", self.check_database_info),
                ("6", "View webhooks", self.view_webhooks),
                ("7", "Find problematic workflows", self.find_problematic_workflows),
                ("8", "Raw SQL shell (advanced)", self.open_database_shell),
                ("9", "Back to main menu", None)
            ]
            
            for key, description, _ in troubleshooting_options:
                print(f"{Colors.GREEN}{key}.{Colors.END} {description}")
            
            print()
            choice = self.get_input("Select troubleshooting option: ", required=False)
            
            if choice == '9':
                break
            
            for key, _, func in troubleshooting_options:
                if choice == key and func:
                    func()
                    break
    
    def check_crashloop_causes(self):
        """Check common crashloop causes"""
        self.print_header("Crashloop Analysis")
        
        self.print_info("Checking pending executions...")
        sql_cmd = "SELECT COUNT(*) FROM execution_entity WHERE status = 'new';"
        db_cmd = f"kubectl exec -it {self.pod_name} -n {self.workspace} -c backup-cron -- sqlite3 database.sqlite \"{sql_cmd}\""
        pending_count = self.run_command(db_cmd)
        
        if pending_count and int(pending_count) > 0:
            print(f"{Colors.RED}⚠ Pending: {pending_count}{Colors.END}")
            if int(pending_count) > 100:
                print(f"{Colors.RED}  HIGH - Could cause crashloop{Colors.END}")
        else:
            print(f"{Colors.GREEN}✓ Pending: 0{Colors.END}")
        
        self.print_info("Checking waiting executions...")
        sql_cmd = "SELECT COUNT(*) FROM execution_entity WHERE status = 'waiting';"
        db_cmd = f"kubectl exec -it {self.pod_name} -n {self.workspace} -c backup-cron -- sqlite3 database.sqlite \"{sql_cmd}\""
        waiting_count = self.run_command(db_cmd)
        
        if waiting_count and int(waiting_count) > 0:
            print(f"{Colors.YELLOW}⚠ Waiting: {waiting_count}{Colors.END}")
        else:
            print(f"{Colors.GREEN}✓ Waiting: 0{Colors.END}")
        
        print()
        self.print_info("Recommendations:")
        if pending_count and int(pending_count) > 100:
            print("  • Cancel pending executions (Option 7)")
        if waiting_count and int(waiting_count) > 0:
            print("  • Cancel waiting executions (Option 8)")
        if not (pending_count and int(pending_count) > 100):
            print("  • Check Grafana for memory issues")
        
        input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")
    
    def view_workflow_history(self):
        """View workflow execution stats"""
        self.print_header("Workflow History")
        
        workflow_id = self.get_input("Workflow ID (or Enter for all): ", required=False)
        
        if workflow_id:
            sql_cmd = f"SELECT status, COUNT(*) FROM execution_entity WHERE workflowId = '{workflow_id}' GROUP BY status;"
            db_cmd = f"kubectl exec -it {self.pod_name} -n {self.workspace} -c backup-cron -- sqlite3 database.sqlite \"{sql_cmd}\""
            print(f"\n{Colors.BOLD}Execution Counts:{Colors.END}")
            self.run_command(db_cmd, capture_output=False)
        else:
            sql_cmd = "SELECT status, COUNT(*) FROM execution_entity GROUP BY status;"
            db_cmd = f"kubectl exec -it {self.pod_name} -n {self.workspace} -c backup-cron -- sqlite3 database.sqlite \"{sql_cmd}\""
            print(f"\n{Colors.BOLD}All Executions:{Colors.END}")
            self.run_command(db_cmd, capture_output=False)
        
        input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")
    
    def list_workflows(self):
        """List all workflows"""
        self.print_header("All Workflows")
        
        sql_cmd = "SELECT id, name, active FROM workflow_entity ORDER BY active DESC, name;"
        db_cmd = f"kubectl exec -it {self.pod_name} -n {self.workspace} -c backup-cron -- sqlite3 database.sqlite \"{sql_cmd}\""
        self.run_command(db_cmd, capture_output=False)
        
        input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")
    
    def view_recent_errors(self):
        """View recent errors"""
        self.print_header("Recent Errors")
        
        limit = self.get_input("Number to show (default 10): ", required=False) or "10"
        
        self.print_info(f"Fetching last {limit} errors...")
        
        print(f"\n{Colors.BOLD}Execution ID | Workflow ID | Workflow Name | Started At{Colors.END}")
        print("-" * 80)
        
        sql_cmd = f"SELECT e.id, e.workflowId, w.name, e.startedAt FROM execution_entity e LEFT JOIN workflow_entity w ON e.workflowId = w.id WHERE e.status IN ('error', 'crashed', 'failed') ORDER BY e.startedAt DESC LIMIT {limit};"
        db_cmd = f"kubectl exec -it {self.pod_name} -n {self.workspace} -c backup-cron -- sqlite3 database.sqlite \"{sql_cmd}\""
        self.run_command(db_cmd, capture_output=False)
        
        print()
        
        if self.confirm("\nView error details for a specific execution?"):
            exec_id = self.get_input("Enter execution ID from the list above: ")
            self.print_info("Fetching error details...")
            
            sql_cmd = f"SELECT data FROM execution_data WHERE executionId = '{exec_id}';"
            result = self.run_db_query(sql_cmd)
            
            if result:
                print(f"\n{Colors.BOLD}Error Details:{Colors.END}")
                print(result)
            elif result is None:
                self.print_warning("Could not fetch error details")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
    
    def check_database_info(self):
        """Check database size"""
        self.print_header("Database Info")
        
        size_cmd = f"kubectl exec -it {self.pod_name} -n {self.workspace} -c backup-cron -- du -sh database.sqlite"
        print(f"\n{Colors.BOLD}Size:{Colors.END}")
        self.run_command(size_cmd, capture_output=False)
        
        tables = [("workflow_entity", "Workflows"), ("execution_entity", "Executions"), 
                  ("webhook_entity", "Webhooks"), ("credentials_entity", "Credentials")]
        
        print(f"\n{Colors.BOLD}Counts:{Colors.END}")
        for table, label in tables:
            sql_cmd = f"SELECT COUNT(*) FROM {table};"
            db_cmd = f"kubectl exec -it {self.pod_name} -n {self.workspace} -c backup-cron -- sqlite3 database.sqlite \"{sql_cmd}\""
            count = self.run_command(db_cmd)
            if count:
                print(f"{label}: {count}")
        
        input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")
    
    def view_webhooks(self):
        """View webhooks"""
        self.print_header("Webhooks")
        
        sql_cmd = "SELECT webhookPath, workflowId, method FROM webhook_entity;"
        db_cmd = f"kubectl exec -it {self.pod_name} -n {self.workspace} -c backup-cron -- sqlite3 database.sqlite \"{sql_cmd}\""
        self.run_command(db_cmd, capture_output=False)
        
        input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")
    
    def find_problematic_workflows(self):
        """Find problematic workflows"""
        self.print_header("Problematic Workflows")
        
        sql_cmd = """
        SELECT w.id, w.name, 
            COUNT(CASE WHEN e.status IN ('error', 'crashed') THEN 1 END) as errors,
            COUNT(*) as total
        FROM execution_entity e
        JOIN workflow_entity w ON e.workflowId = w.id
        GROUP BY w.id
        HAVING errors > 0
        ORDER BY errors DESC
        LIMIT 10;
        """
        db_cmd = f"kubectl exec -it {self.pod_name} -n {self.workspace} -c backup-cron -- sqlite3 database.sqlite \"{sql_cmd}\""
        self.run_command(db_cmd, capture_output=False)
        
        input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")
    
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
        self.print_header("Database Shell (Advanced)")
        
        self.print_info("Opening SQLite shell...")
        self.print_warning("Type .quit to exit")
        self.print_info("Tip: Use .tables to list tables, .schema <table> to view structure")
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
