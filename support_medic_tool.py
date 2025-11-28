#!/usr/bin/env python3
"""
Cloud Medic Assistant Tool v1.4
Interactive CLI for n8n Cloud Support operations

Changelog v1.4:
- Added OOM Investigation (Database Troubleshooting → Option 9)
- Automatic analysis of database metrics, execution patterns, and memory pressure
- "Likely culprits" analysis with actionable recommendations
- kubectl commands for manual Grafana/log investigation

Changelog v1.3:
- Added pre-menu for operation mode selection
- Added deleted instance recovery menu (list/export workflows from backups)
- Fixed: Block pod-required operations when Pod: None
- Fixed: Export workflows now properly validates success/failure

Changelog v1.2.2:
- Fixed: Graceful error handling when changing workspace/cluster and pod not found

Changelog v1.2.1:
- Fixed: Export from backup now uses backup's date in filename instead of today's date

Changelog v1.2:
- Added execution status checker with year 3000 detection
- Added log download menu (n8n, backup, k8s, execution, bundle)
- Added disable 2FA feature
- Added change owner email feature
- Sanitized all documentation

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
        self.deleted_instance_mode = False  # New flag for deleted instance recovery mode

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

    def print_section_header(self, title):
        """Print a section header for OOM investigation"""
        print()
        print("─" * 65)
        print(title)
        print("─" * 65)

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

    def run_db_query_rows(self, sql_query):
        """Run SQL query and return list of rows (pipe-separated)"""
        # Escape single quotes in SQL
        sql_escaped = sql_query.replace("'", "'\\''")

        cmd = f"kubectl exec -it {self.pod_name} -n {self.workspace} -c backup-cron -- sqlite3 -separator '|' database.sqlite \"{sql_escaped}\""

        result = self.run_command(cmd)

        if result:
            # Split into lines, filter empty
            lines = [line.strip() for line in result.strip().split('\n') if line.strip()]
            return lines
        return []

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

    def find_pod(self):
        """Find pod name for current workspace"""
        pod_cmd = f"kubectl get pods -n {self.workspace} -o jsonpath='{{.items[0].metadata.name}}'"
        pod_name = self.run_command(pod_cmd)
        return pod_name if pod_name else None

    def setup_workspace(self):
        """Get workspace name and cluster information"""
        self.print_header("Cloud Medic Assistant - Setup v1.4")

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
        self.pod_name = self.find_pod()

        if self.pod_name:
            self.print_success(f"Found pod: {self.pod_name}")
            return True
        else:
            self.print_error("Could not find pod. Please verify workspace name.")
            return False

    def change_workspace_cluster(self):
        """Change to a different workspace/cluster with proper error handling"""
        self.print_header("Change Workspace/Cluster")

        # Store current state for potential rollback
        old_workspace = self.workspace
        old_cluster = self.cluster
        old_cluster_number = self.cluster_number
        old_pod = self.pod_name

        # Get new workspace
        new_workspace = self.get_input("Enter workspace name: ")
        cluster_num = self.get_input("Enter cluster number (e.g., 48 for prod-users-gwc-48): ")
        new_cluster = f"prod-users-gwc-{cluster_num}"

        # Switch cluster
        self.print_info(f"Switching to cluster {new_cluster}...")
        result = self.run_command(f"kubectx {new_cluster}", capture_output=True)

        if result is None:
            self.print_error(f"Failed to switch to cluster {new_cluster}")
            self.print_warning("Staying on current workspace")
            input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")
            return

        self.print_success(f"Switched to cluster: {new_cluster}")

        # Temporarily update state for pod search
        self.workspace = new_workspace
        self.cluster = new_cluster
        self.cluster_number = cluster_num

        # Find pod
        self.print_info(f"Finding pod for workspace: {new_workspace}...")
        new_pod = self.find_pod()

        # Handle pod not found gracefully
        if not new_pod:
            self.print_error(f"Could not find pod for workspace: {new_workspace}")
            print()
            print(f"{Colors.YELLOW}Possible reasons:{Colors.END}")
            print("  • Workspace name is incorrect")
            print("  • Workspace doesn't exist in this cluster")
            print("  • Instance is not deployed")
            print()
            print(f"{Colors.BOLD}Options:{Colors.END}")
            print("1. Try different workspace/cluster")
            print("2. Revert to previous workspace")
            print("3. Continue anyway (limited operations)")
            print()

            choice = self.get_input("Select option (1/2/3): ")

            if choice == "1":
                # Rollback state first
                self.workspace = old_workspace
                self.cluster = old_cluster
                self.cluster_number = old_cluster_number
                self.pod_name = old_pod
                self.run_command(f"kubectx {old_cluster}", capture_output=True)

                # Recursively call to try again
                self.change_workspace_cluster()
                return

            elif choice == "2":
                # Rollback to previous workspace
                self.print_info(f"Reverting to {old_workspace} in {old_cluster}...")
                self.workspace = old_workspace
                self.cluster = old_cluster
                self.cluster_number = old_cluster_number
                self.pod_name = old_pod
                self.run_command(f"kubectx {old_cluster}", capture_output=True)
                self.print_success("Reverted to previous workspace")
                input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")
                return

            elif choice == "3":
                # Continue with no pod (limited operations)
                self.print_warning("Continuing with limited operations")
                self.pod_name = None
                print()
                print(f"{Colors.BOLD}Available operations:{Colors.END}")
                print("  • Export from backup (Option 2)")
                print("  • Change workspace/cluster (Option 13)")
                print()
                print(f"{Colors.YELLOW}⚠ All other operations require a valid pod{Colors.END}")
                input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")
                return

            else:
                # Invalid choice, rollback to be safe
                self.print_info("Invalid choice. Reverting to previous workspace...")
                self.workspace = old_workspace
                self.cluster = old_cluster
                self.cluster_number = old_cluster_number
                self.pod_name = old_pod
                self.run_command(f"kubectx {old_cluster}", capture_output=True)
                self.print_success("Reverted to previous workspace")
                input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")
                return

        # Success - pod found
        self.pod_name = new_pod
        self.print_success(f"Found pod: {new_pod}")
        self.print_success(f"Successfully switched to workspace: {new_workspace}")

        input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")

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
            ("13", "Change workspace/cluster", self.change_workspace_cluster),
            ("14", "Download logs", self.download_logs),
            ("15", "Disable 2FA", self.disable_2fa),
            ("16", "Change owner email", self.change_owner_email),
            ("q", "Quit", None)
        ]

        for key, description, _ in menu_options:
            print(f"{Colors.GREEN}{key}.{Colors.END} {description}")

        print()
        choice = self.get_input("Select an option: ", required=False)

        # Pod-required operation check (Bug Fix #1)
        pod_not_required = ['2', '13']  # Export from backup, change workspace

        if choice not in pod_not_required and choice != 'q' and not self.pod_name:
            self.print_error("This operation requires a valid pod")
            print()
            print(f"{Colors.BOLD}Pod is not available for workspace: {self.workspace}{Colors.END}")
            print()
            print(f"{Colors.BOLD}Available options without pod:{Colors.END}")
            print("  • Option 2: Export from backup")
            print("  • Option 13: Change workspace/cluster")
            print("  • Option q: Quit")
            input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")
            return True

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
                ("8", "Check executions by status", self.check_execution_status),
                ("9", "Investigate OOM cause", self.investigate_oom),
                ("10", "Raw SQL shell (advanced)", self.open_database_shell),
                ("11", "Back to main menu", None)
            ]

            for key, description, _ in troubleshooting_options:
                print(f"{Colors.GREEN}{key}.{Colors.END} {description}")

            print()
            choice = self.get_input("Select troubleshooting option: ", required=False)

            if choice == '11':
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

    # ============================================================
    # Feature 1: Execution Status Checker
    # ============================================================

    def check_execution_status(self):
        """Check executions by status with detailed analysis"""
        while True:
            self.print_header("Execution Status Checker")

            status_options = [
                ("1", "Waiting executions", self.check_waiting_executions_detailed),
                ("2", "Pending/New executions", self.check_pending_executions_detailed),
                ("3", "Running executions", self.check_running_executions),
                ("4", "Error/Failed executions", self.check_error_executions),
                ("5", "All statuses summary", self.check_all_statuses_summary),
                ("6", "Back to troubleshooting menu", None)
            ]

            for key, description, _ in status_options:
                print(f"{Colors.GREEN}{key}.{Colors.END} {description}")

            choice = self.get_input("Select option: ", required=False)

            if choice == '6':
                break

            for key, _, func in status_options:
                if choice == key and func:
                    func()
                    break

    def check_waiting_executions_detailed(self):
        """Detailed analysis of waiting executions"""
        self.print_header("Waiting Executions Analysis")

        # Count total
        count_sql = "SELECT COUNT(*) FROM execution_entity WHERE status = 'waiting';"
        total = self.run_db_query(count_sql)

        if not total or total == "0":
            self.print_success("No waiting executions")
            input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")
            return

        self.print_info(f"Total waiting: {total}")

        # Check for "year 3000" stuck executions
        stuck_sql = """
SELECT
    e.id,
    w.name as workflow_name,
    e.workflowId,
    e.startedAt,
    e.waitTill,
    ROUND((julianday('now') - julianday(e.startedAt))) as days_waiting
FROM execution_entity e
LEFT JOIN workflow_entity w ON e.workflowId = w.id
WHERE e.status = 'waiting'
AND e.waitTill = '3000-01-01 00:00:00.000'
ORDER BY e.startedAt ASC;
"""

        print(f"\n{Colors.BOLD}STUCK EXECUTIONS (waiting until year 3000):{Colors.END}")
        result = self.run_db_query(stuck_sql)

        if result:
            # Parse and group by workflow
            lines = result.strip().split('\n')
            workflows = {}
            for line in lines:
                parts = line.split('|')
                if len(parts) >= 3:
                    exec_id = parts[0]
                    wf_name = parts[1] if parts[1] else "Unknown"
                    wf_id = parts[2]
                    started = parts[3] if len(parts) > 3 else "Unknown"
                    days = parts[5] if len(parts) > 5 else "?"

                    if wf_name not in workflows:
                        workflows[wf_name] = []
                    workflows[wf_name].append({
                        'id': exec_id,
                        'started': started,
                        'days': days
                    })

            # Display grouped by workflow
            for wf_name, execs in workflows.items():
                print(f"\n  {Colors.YELLOW}Workflow:{Colors.END} {wf_name}")
                for exec in execs:
                    print(f"    • Execution {exec['id']} - Started {exec['started']} ({exec['days']} days ago)")
                print(f"    {Colors.BOLD}Total: {len(execs)} executions{Colors.END}")
        else:
            print(f"  {Colors.GREEN}None{Colors.END}")

        # Check for normal waiting (will resume)
        normal_sql = """
SELECT COUNT(*) FROM execution_entity
WHERE status = 'waiting'
AND waitTill != '3000-01-01 00:00:00.000'
AND datetime(waitTill) > datetime('now');
"""
        normal_count = self.run_db_query(normal_sql)

        print(f"\n{Colors.BOLD}NORMAL WAITING (will resume):{Colors.END}")
        if normal_count and int(normal_count) > 0:
            print(f"  {normal_count} executions")
        else:
            print(f"  {Colors.GREEN}None{Colors.END}")

        # Recommendations
        print(f"\n{Colors.BOLD}Recommendations:{Colors.END}")
        if result:  # Has stuck executions
            print(f"  • These executions are stuck indefinitely")
            print(f"  • Consider canceling them (Main Menu → Option 8)")
            print(f"  • Check workflow configurations for Wait nodes")
        else:
            print(f"  {Colors.GREEN}All waiting executions look normal{Colors.END}")

        input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")

    def check_pending_executions_detailed(self):
        """Detailed analysis of pending/new executions"""
        self.print_header("Pending Executions Analysis")

        # Count total
        count_sql = "SELECT COUNT(*) FROM execution_entity WHERE status = 'new';"
        total = self.run_db_query(count_sql)

        if not total or total == "0":
            self.print_success("No pending executions")
            input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")
            return

        self.print_info(f"Total pending: {total}")

        # Group by workflow
        by_workflow_sql = """
SELECT
    w.name as workflow_name,
    e.workflowId,
    COUNT(*) as count
FROM execution_entity e
LEFT JOIN workflow_entity w ON e.workflowId = w.id
WHERE e.status = 'new'
GROUP BY e.workflowId, w.name
ORDER BY count DESC
LIMIT 10;
"""

        print(f"\n{Colors.BOLD}By Workflow:{Colors.END}")
        result = self.run_db_query(by_workflow_sql)

        if result:
            for line in result.strip().split('\n'):
                parts = line.split('|')
                if len(parts) >= 3:
                    wf_name = parts[0] if parts[0] else "Unknown"
                    count = parts[2]
                    if int(count) > 100:
                        print(f"  {Colors.RED}{wf_name}: {count} executions (HIGH!){Colors.END}")
                    elif int(count) > 50:
                        print(f"  {Colors.YELLOW}{wf_name}: {count} executions{Colors.END}")
                    else:
                        print(f"  • {wf_name}: {count} executions")

        # Recommendations
        print(f"\n{Colors.BOLD}Recommendations:{Colors.END}")
        if total and int(total) > 100:
            print(f"  {Colors.RED}HIGH: More than 100 pending can cause crashloop{Colors.END}")
            print(f"  • Cancel pending executions (Main Menu → Option 7)")
            print(f"  • Check for workflow execution loops")
        elif total and int(total) > 50:
            print(f"  {Colors.YELLOW}MEDIUM: Monitor this closely{Colors.END}")
        else:
            print(f"  {Colors.GREEN}Pending count looks normal{Colors.END}")

        input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")

    def check_running_executions(self):
        """Check currently running executions"""
        self.print_header("Running Executions")

        sql = """
SELECT
    e.id,
    w.name as workflow_name,
    e.startedAt,
    ROUND((julianday('now') - julianday(e.startedAt)) * 24 * 60) as minutes_running
FROM execution_entity e
LEFT JOIN workflow_entity w ON e.workflowId = w.id
WHERE e.status = 'running'
ORDER BY e.startedAt ASC
LIMIT 20;
"""

        result = self.run_db_query(sql)

        if not result:
            self.print_success("No running executions")
            input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")
            return

        print(f"\n{Colors.BOLD}Currently Running:{Colors.END}\n")

        for line in result.strip().split('\n'):
            parts = line.split('|')
            if len(parts) >= 4:
                exec_id = parts[0]
                wf_name = parts[1] if parts[1] else "Unknown"
                started = parts[2]
                minutes = parts[3]

                if minutes and float(minutes) > 60:
                    print(f"  {Colors.YELLOW}Execution {exec_id}{Colors.END}")
                    print(f"    Workflow: {wf_name}")
                    print(f"    Running: {minutes} minutes (unusually long!)")
                else:
                    print(f"  • Execution {exec_id} - {wf_name} ({minutes} min)")

        input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")

    def check_error_executions(self):
        """Detailed error execution analysis"""
        self.print_header("Error Analysis")

        # Count by status
        count_sql = """
SELECT status, COUNT(*) as count
FROM execution_entity
WHERE status IN ('error', 'crashed', 'failed')
GROUP BY status;
"""

        print(f"\n{Colors.BOLD}Error Counts:{Colors.END}")
        result = self.run_db_query(count_sql)

        if result:
            for line in result.strip().split('\n'):
                parts = line.split('|')
                if len(parts) >= 2:
                    status = parts[0]
                    count = parts[1]
                    print(f"  {status}: {count}")

        # By workflow
        by_workflow_sql = """
SELECT
    w.name as workflow_name,
    COUNT(*) as error_count
FROM execution_entity e
LEFT JOIN workflow_entity w ON e.workflowId = w.id
WHERE e.status IN ('error', 'crashed', 'failed')
GROUP BY w.name
ORDER BY error_count DESC
LIMIT 10;
"""

        print(f"\n{Colors.BOLD}Top Error Workflows:{Colors.END}")
        result = self.run_db_query(by_workflow_sql)

        if result:
            for line in result.strip().split('\n'):
                parts = line.split('|')
                if len(parts) >= 2:
                    wf_name = parts[0] if parts[0] else "Unknown"
                    count = parts[1]
                    print(f"  • {wf_name}: {count} errors")

        # Recent errors
        recent_sql = """
SELECT
    e.id,
    w.name as workflow_name,
    e.status,
    e.startedAt
FROM execution_entity e
LEFT JOIN workflow_entity w ON e.workflowId = w.id
WHERE e.status IN ('error', 'crashed', 'failed')
ORDER BY e.startedAt DESC
LIMIT 10;
"""

        print(f"\n{Colors.BOLD}Recent Errors:{Colors.END}")
        result = self.run_db_query(recent_sql)

        if result:
            for line in result.strip().split('\n'):
                parts = line.split('|')
                if len(parts) >= 4:
                    exec_id = parts[0]
                    wf_name = parts[1] if parts[1] else "Unknown"
                    status = parts[2]
                    started = parts[3]
                    print(f"  • {exec_id} - {wf_name} ({status}) - {started}")

        input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")

    def check_all_statuses_summary(self):
        """Show summary of all execution statuses"""
        self.print_header("All Statuses Summary")

        sql = """
SELECT status, COUNT(*) as count
FROM execution_entity
GROUP BY status
ORDER BY count DESC;
"""

        result = self.run_db_query(sql)

        if not result:
            self.print_error("No execution data")
            input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")
            return

        print(f"\n{Colors.BOLD}Execution Counts by Status:{Colors.END}\n")

        for line in result.strip().split('\n'):
            parts = line.split('|')
            if len(parts) >= 2:
                status = parts[0]
                count = parts[1]

                # Color code based on status
                if status in ['error', 'crashed', 'failed']:
                    print(f"  {Colors.RED}{status:<15}{Colors.END} {count}")
                elif status in ['waiting', 'new']:
                    print(f"  {Colors.YELLOW}{status:<15}{Colors.END} {count}")
                elif status == 'running':
                    print(f"  {Colors.BLUE}{status:<15}{Colors.END} {count}")
                elif status == 'success':
                    print(f"  {Colors.GREEN}{status:<15}{Colors.END} {count}")
                else:
                    print(f"  {status:<15} {count}")

        input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")

    # ============================================================
    # Feature: OOM Investigation
    # ============================================================

    def investigate_oom(self):
        """Investigate OOM (Out of Memory) crash causes"""
        self.print_header("OOM INVESTIGATION")

        print("Gathering data... please wait.\n")

        # 1. DATABASE METRICS
        self.print_section_header("📊 DATABASE METRICS")

        # Database size
        size_cmd = f"kubectl exec -it {self.pod_name} -n {self.workspace} -c backup-cron -- du -sh database.sqlite 2>/dev/null | awk '{{print $1}}'"
        db_size = self.run_command(size_cmd)

        # Total executions
        total_exec = self.run_db_query("SELECT COUNT(*) FROM execution_entity;")

        # Active workflows
        active_wf = self.run_db_query("SELECT COUNT(*) FROM workflow_entity WHERE active = 1;")

        print(f"Database Size:        {db_size or 'Unknown'}")
        print(f"Total Executions:     {total_exec or 'Unknown'}")
        print(f"Active Workflows:     {active_wf or 'Unknown'}")

        # 2. TOP WORKFLOWS BY EXECUTION COUNT
        self.print_section_header("🔥 TOP WORKFLOWS BY EXECUTION COUNT (Last 24h)")

        top_workflows_sql = """
        SELECT
            e.workflowId,
            COALESCE(w.name, 'Unknown') as name,
            COUNT(*) as exec_count
        FROM execution_entity e
        LEFT JOIN workflow_entity w ON e.workflowId = w.id
        WHERE datetime(e.startedAt) > datetime('now', '-1 day')
        GROUP BY e.workflowId
        ORDER BY exec_count DESC
        LIMIT 5;
        """

        top_workflows = self.run_db_query_rows(top_workflows_sql)

        print(f"{'ID':<20} {'Name':<30} {'Executions':<10}")
        print("─" * 62)

        if top_workflows:
            for row in top_workflows:
                wf_id, name, count = row.split('|')
                # Truncate name if too long
                name = name[:28] + '..' if len(name) > 30 else name
                print(f"{wf_id:<20} {name:<30} {count:<10}")
        else:
            print("No executions in the last 24 hours")

        # 3. WORKFLOWS WITH ERRORS
        self.print_section_header("⚠️  WORKFLOWS WITH RECENT ERRORS (Last 24h)")

        error_workflows_sql = """
        SELECT
            e.workflowId,
            COALESCE(w.name, 'Unknown') as name,
            COUNT(*) as error_count
        FROM execution_entity e
        LEFT JOIN workflow_entity w ON e.workflowId = w.id
        WHERE e.status IN ('error', 'crashed', 'failed')
        AND datetime(e.startedAt) > datetime('now', '-1 day')
        GROUP BY e.workflowId
        HAVING error_count > 0
        ORDER BY error_count DESC
        LIMIT 5;
        """

        error_workflows = self.run_db_query_rows(error_workflows_sql)

        print(f"{'ID':<20} {'Name':<30} {'Errors':<10}")
        print("─" * 62)

        if error_workflows:
            for row in error_workflows:
                wf_id, name, count = row.split('|')
                name = name[:28] + '..' if len(name) > 30 else name
                print(f"{wf_id:<20} {name:<30} {count:<10}")
        else:
            print("No workflow errors in the last 24 hours")

        # 4. EXECUTION QUEUE STATUS
        self.print_section_header("⏳ EXECUTION QUEUE STATUS")

        pending_count = self.run_db_query("SELECT COUNT(*) FROM execution_entity WHERE status = 'new';")
        waiting_count = self.run_db_query("SELECT COUNT(*) FROM execution_entity WHERE status = 'waiting';")
        running_count = self.run_db_query("SELECT COUNT(*) FROM execution_entity WHERE status = 'running';")

        pending_int = int(pending_count) if pending_count else 0
        waiting_int = int(waiting_count) if waiting_count else 0
        running_int = int(running_count) if running_count else 0

        pending_warning = " ⚠️  HIGH - may cause memory pressure" if pending_int > 100 else ""

        print(f"Pending ('new'):      {pending_int}{pending_warning}")
        print(f"Waiting:              {waiting_int}")
        print(f"Running:              {running_int}")

        # 5. EXECUTION GROWTH
        self.print_section_header("📈 EXECUTION GROWTH (Last 7 Days)")

        growth_sql = """
        SELECT
            date(startedAt) as day,
            COUNT(*) as executions
        FROM execution_entity
        WHERE datetime(startedAt) > datetime('now', '-7 days')
        GROUP BY date(startedAt)
        ORDER BY day DESC;
        """

        growth_data = self.run_db_query_rows(growth_sql)

        print(f"{'Date':<15} {'Executions':<10}")
        print("─" * 25)

        if growth_data:
            for row in growth_data:
                day, count = row.split('|')
                print(f"{day:<15} {count:<10}")
        else:
            print("No execution data available")

        # 6. LIKELY CULPRITS ANALYSIS
        self.print_section_header("🎯 LIKELY CULPRITS")

        culprits = []

        # Check for high execution volume workflow
        if top_workflows:
            first_wf = top_workflows[0].split('|')
            wf_id, wf_name, exec_count = first_wf[0], first_wf[1], int(first_wf[2])

            if exec_count > 500:
                # Check if this workflow also has errors
                error_count = 0
                if error_workflows:
                    for row in error_workflows:
                        parts = row.split('|')
                        if parts[0] == wf_id:
                            error_count = int(parts[2])
                            break

                culprits.append({
                    'type': 'HIGH_EXECUTION_VOLUME',
                    'workflow_id': wf_id,
                    'workflow_name': wf_name,
                    'exec_count': exec_count,
                    'error_count': error_count
                })

        # Check for pending backlog
        if pending_int > 100:
            culprits.append({
                'type': 'PENDING_BACKLOG',
                'count': pending_int
            })

        # Check for large database
        if db_size:
            # Parse size (e.g., "245M" or "1.2G")
            size_str = db_size.strip()
            size_num = float(size_str[:-1]) if size_str else 0
            size_unit = size_str[-1] if size_str else 'M'

            size_mb = size_num if size_unit == 'M' else size_num * 1024 if size_unit == 'G' else size_num / 1024

            if size_mb > 200:
                culprits.append({
                    'type': 'LARGE_DATABASE',
                    'size': db_size
                })

        # Check for error-prone workflow
        if error_workflows:
            first_error_wf = error_workflows[0].split('|')
            err_wf_id, err_wf_name, err_count = first_error_wf[0], first_error_wf[1], int(first_error_wf[2])

            if err_count > 50:
                # Only add if not already added as high execution volume
                already_added = any(c.get('workflow_id') == err_wf_id for c in culprits)
                if not already_added:
                    culprits.append({
                        'type': 'ERROR_PRONE_WORKFLOW',
                        'workflow_id': err_wf_id,
                        'workflow_name': err_wf_name,
                        'error_count': err_count
                    })

        # Display culprits
        if culprits:
            for i, culprit in enumerate(culprits, 1):
                print()
                if culprit['type'] == 'HIGH_EXECUTION_VOLUME':
                    print(f"{i}. ⚠️  HIGH EXECUTION VOLUME: \"{culprit['workflow_name']}\" ({culprit['workflow_id']})")
                    error_msg = f" with {culprit['error_count']} errors" if culprit['error_count'] > 0 else ""
                    print(f"   → {culprit['exec_count']} executions in 24h{error_msg}")
                    print(f"   → Recommendation: Check if processing large data payloads")
                    if culprit['error_count'] > 0:
                        print(f"   → Recommendation: Review for infinite loops or retries")

                elif culprit['type'] == 'PENDING_BACKLOG':
                    print(f"{i}. ⚠️  PENDING EXECUTION BACKLOG: {culprit['count']} pending")
                    print(f"   → These pile up and consume memory on startup")
                    print(f"   → Recommendation: Cancel pending executions (Main Menu → Option 7)")

                elif culprit['type'] == 'LARGE_DATABASE':
                    print(f"{i}. ⚠️  DATABASE SIZE: {culprit['size']}")
                    print(f"   → Large databases slow down startup and queries")
                    print(f"   → Recommendation: Consider pruning old executions")

                elif culprit['type'] == 'ERROR_PRONE_WORKFLOW':
                    print(f"{i}. ⚠️  ERROR-PRONE WORKFLOW: \"{culprit['workflow_name']}\" ({culprit['workflow_id']})")
                    print(f"   → {culprit['error_count']} errors in last 24h")
                    print(f"   → Recommendation: Workflow may be retrying repeatedly, consuming memory")
        else:
            print("\nNo obvious culprits detected from database analysis.")
            print("Check Grafana memory metrics for runtime memory spikes.")

        # 7. MANUAL CHECKS
        self.print_section_header("📋 MANUAL CHECKS (Grafana / kubectl)")

        print("\nRun these commands for additional context:\n")
        print("# Memory usage over time (check Grafana)")
        print("Dashboard: n8n Cloud → Instance Metrics → Memory\n")
        print("# Pod events (OOMKill timestamps)")
        print(f"kubectl describe pod {self.pod_name} -n {self.workspace} | grep -A 15 Events\n")
        print("# Logs before crash")
        print(f"kubectl logs {self.pod_name} -c n8n --previous --tail=100\n")
        print("# Current memory usage")
        print(f"kubectl top pod {self.pod_name} -n {self.workspace}\n")

        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

    # ============================================================
    # Feature 2: Log Download Menu
    # ============================================================

    def download_logs(self):
        """Log download menu"""
        while True:
            self.print_header("Log Download")

            log_options = [
                ("1", "n8n container logs", self.download_n8n_logs),
                ("2", "backup-cron logs", self.download_backup_logs),
                ("3", "Kubernetes events", self.download_k8s_events),
                ("4", "Execution logs (by ID)", self.download_execution_logs),
                ("5", "All logs (bundle)", self.download_all_logs),
                ("6", "Back to main menu", None)
            ]

            for key, description, _ in log_options:
                print(f"{Colors.GREEN}{key}.{Colors.END} {description}")

            print()
            choice = self.get_input("Select option: ", required=False)

            if choice == '6':
                break

            for key, _, func in log_options:
                if choice == key and func:
                    func()
                    break

    def download_n8n_logs(self):
        """Download n8n container logs with timeframe options"""
        self.print_header("Download n8n Logs")

        print("Choose timeframe:")
        print("1. Last 100 lines")
        print("2. Last 500 lines")
        print("3. Last 1000 lines")
        print("4. Last 1 hour")
        print("5. Last 24 hours")
        print("6. All available")
        print("7. Custom line count")

        choice = self.get_input("\nSelect: ")

        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")

        if choice == "1":
            tail = "100"
            filename = f"{self.workspace}-n8n-logs-100-{timestamp}.txt"
            cmd = f"kubectl logs {self.pod_name} -n {self.workspace} -c n8n --tail={tail}"
        elif choice == "2":
            tail = "500"
            filename = f"{self.workspace}-n8n-logs-500-{timestamp}.txt"
            cmd = f"kubectl logs {self.pod_name} -n {self.workspace} -c n8n --tail={tail}"
        elif choice == "3":
            tail = "1000"
            filename = f"{self.workspace}-n8n-logs-1000-{timestamp}.txt"
            cmd = f"kubectl logs {self.pod_name} -n {self.workspace} -c n8n --tail={tail}"
        elif choice == "4":
            filename = f"{self.workspace}-n8n-logs-1h-{timestamp}.txt"
            cmd = f"kubectl logs {self.pod_name} -n {self.workspace} -c n8n --since=1h"
        elif choice == "5":
            filename = f"{self.workspace}-n8n-logs-24h-{timestamp}.txt"
            cmd = f"kubectl logs {self.pod_name} -n {self.workspace} -c n8n --since=24h"
        elif choice == "6":
            filename = f"{self.workspace}-n8n-logs-all-{timestamp}.txt"
            cmd = f"kubectl logs {self.pod_name} -n {self.workspace} -c n8n"
        elif choice == "7":
            custom = self.get_input("Enter line count: ")
            filename = f"{self.workspace}-n8n-logs-{custom}-{timestamp}.txt"
            cmd = f"kubectl logs {self.pod_name} -n {self.workspace} -c n8n --tail={custom}"
        else:
            self.print_error("Invalid choice")
            input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")
            return

        filepath = self.downloads_dir / filename

        self.print_info("Downloading logs...")
        full_cmd = f"{cmd} > {filepath}"
        result = self.run_command(full_cmd, capture_output=False)

        if filepath.exists():
            file_size = filepath.stat().st_size / 1024  # KB
            self.print_success(f"Downloaded: {filename} ({file_size:.1f} KB)")
            self.print_info(f"Location: {filepath}")
        else:
            self.print_error("Download failed")

        # Offer to check previous logs if pod restarted
        if self.confirm("\nCheck if previous container logs exist? (if pod restarted)"):
            prev_filename = f"{self.workspace}-n8n-logs-previous-{timestamp}.txt"
            prev_filepath = self.downloads_dir / prev_filename
            prev_cmd = f"kubectl logs {self.pod_name} -n {self.workspace} -c n8n --previous > {prev_filepath} 2>&1"

            self.print_info("Checking for previous logs...")
            self.run_command(prev_cmd, capture_output=False, check=False)

            if prev_filepath.exists() and prev_filepath.stat().st_size > 0:
                prev_size = prev_filepath.stat().st_size / 1024
                self.print_success(f"Previous logs saved: {prev_filename} ({prev_size:.1f} KB)")
            else:
                self.print_info("No previous logs available (pod hasn't restarted)")
                if prev_filepath.exists():
                    prev_filepath.unlink()

        input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")

    def download_backup_logs(self):
        """Download backup-cron container logs"""
        self.print_header("Download Backup Logs")

        lines = self.get_input("Number of lines (default 500): ", required=False) or "500"

        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        filename = f"{self.workspace}-backup-logs-{timestamp}.txt"
        filepath = self.downloads_dir / filename

        self.print_info("Downloading backup logs...")
        cmd = f"kubectl logs {self.pod_name} -n {self.workspace} -c backup-cron --tail={lines} > {filepath}"
        result = self.run_command(cmd, capture_output=False)

        if filepath.exists():
            file_size = filepath.stat().st_size / 1024
            self.print_success(f"Downloaded: {filename} ({file_size:.1f} KB)")
            self.print_info(f"Location: {filepath}")
        else:
            self.print_error("Download failed")

        input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")

    def download_k8s_events(self):
        """Download Kubernetes events for the namespace"""
        self.print_header("Download Kubernetes Events")

        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")

        # Events
        events_filename = f"{self.workspace}-k8s-events-{timestamp}.txt"
        events_filepath = self.downloads_dir / events_filename

        self.print_info("Downloading Kubernetes events...")
        events_cmd = f"kubectl get events -n {self.workspace} --sort-by='.lastTimestamp' > {events_filepath}"
        self.run_command(events_cmd, capture_output=False)

        # Pod describe
        describe_filename = f"{self.workspace}-pod-describe-{timestamp}.txt"
        describe_filepath = self.downloads_dir / describe_filename

        self.print_info("Downloading pod description...")
        describe_cmd = f"kubectl describe pod {self.pod_name} -n {self.workspace} > {describe_filepath}"
        self.run_command(describe_cmd, capture_output=False)

        # Summary
        print(f"\n{Colors.BOLD}Downloaded:{Colors.END}")
        if events_filepath.exists():
            size = events_filepath.stat().st_size / 1024
            print(f"  • {events_filename} ({size:.1f} KB)")
        if describe_filepath.exists():
            size = describe_filepath.stat().st_size / 1024
            print(f"  • {describe_filename} ({size:.1f} KB)")

        input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")

    def download_execution_logs(self):
        """Download logs for a specific execution"""
        self.print_header("Download Execution Logs")

        execution_id = self.get_input("Enter execution ID: ")

        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        filename = f"{self.workspace}-execution-{execution_id}-{timestamp}.json"
        filepath = self.downloads_dir / filename

        self.print_info(f"Fetching execution data for ID: {execution_id}...")

        # Get execution data
        sql_cmd = f"SELECT data FROM execution_data WHERE executionId = '{execution_id}';"
        result = self.run_db_query(sql_cmd)

        if result:
            # Write to file
            with open(filepath, 'w') as f:
                f.write(result)

            file_size = filepath.stat().st_size / 1024
            self.print_success(f"Downloaded: {filename} ({file_size:.1f} KB)")
            self.print_info(f"Location: {filepath}")
        else:
            self.print_error(f"No data found for execution ID: {execution_id}")

        input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")

    def download_all_logs(self):
        """Download all logs as a bundle"""
        self.print_header("Download All Logs (Bundle)")

        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        bundle_dir = Path(f"/tmp/logs-bundle-{timestamp}")
        bundle_dir.mkdir(exist_ok=True)

        self.print_info("Creating log bundle...")

        files_created = []

        # n8n logs
        self.print_info("  • n8n container logs...")
        n8n_file = bundle_dir / "n8n-logs.txt"
        cmd = f"kubectl logs {self.pod_name} -n {self.workspace} -c n8n --tail=1000 > {n8n_file}"
        if self.run_command(cmd, capture_output=False, check=False) is not None:
            if n8n_file.exists():
                files_created.append(("n8n-logs.txt", n8n_file.stat().st_size))

        # backup logs
        self.print_info("  • backup-cron logs...")
        backup_file = bundle_dir / "backup-logs.txt"
        cmd = f"kubectl logs {self.pod_name} -n {self.workspace} -c backup-cron --tail=500 > {backup_file}"
        if self.run_command(cmd, capture_output=False, check=False) is not None:
            if backup_file.exists():
                files_created.append(("backup-logs.txt", backup_file.stat().st_size))

        # k8s events
        self.print_info("  • Kubernetes events...")
        events_file = bundle_dir / "k8s-events.txt"
        cmd = f"kubectl get events -n {self.workspace} --sort-by='.lastTimestamp' > {events_file}"
        if self.run_command(cmd, capture_output=False, check=False) is not None:
            if events_file.exists():
                files_created.append(("k8s-events.txt", events_file.stat().st_size))

        # pod describe
        self.print_info("  • Pod description...")
        describe_file = bundle_dir / "pod-describe.txt"
        cmd = f"kubectl describe pod {self.pod_name} -n {self.workspace} > {describe_file}"
        if self.run_command(cmd, capture_output=False, check=False) is not None:
            if describe_file.exists():
                files_created.append(("pod-describe.txt", describe_file.stat().st_size))

        # execution summary
        self.print_info("  • Execution summary...")
        exec_file = bundle_dir / "execution-summary.txt"
        sql_cmd = "SELECT status, COUNT(*) FROM execution_entity GROUP BY status;"
        result = self.run_db_query(sql_cmd, show_error_details=False)
        if result:
            with open(exec_file, 'w') as f:
                f.write("Execution Status Summary\n")
                f.write("========================\n\n")
                f.write(result)
            files_created.append(("execution-summary.txt", exec_file.stat().st_size))

        # Create tar.gz
        self.print_info("  • Creating archive...")
        bundle_filename = f"{self.workspace}-logs-bundle-{timestamp}.tar.gz"
        bundle_filepath = self.downloads_dir / bundle_filename

        tar_cmd = f"tar -czf {bundle_filepath} -C {bundle_dir} ."
        self.run_command(tar_cmd, capture_output=False)

        # Cleanup temp directory
        import shutil
        shutil.rmtree(bundle_dir)

        # Summary
        if bundle_filepath.exists():
            bundle_size = bundle_filepath.stat().st_size / 1024
            self.print_success(f"Bundle created: {bundle_filename} ({bundle_size:.1f} KB)")
            self.print_info(f"Location: {bundle_filepath}")

            print(f"\n{Colors.BOLD}Contents:{Colors.END}")
            for filename, size in files_created:
                print(f"  • {filename} ({size / 1024:.1f} KB)")
        else:
            self.print_error("Bundle creation failed")

        input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")

    # ============================================================
    # Feature 3: Disable 2FA
    # ============================================================

    def disable_2fa(self):
        """Disable 2FA for a user"""
        self.print_header("Disable 2FA")

        # Get user email
        user_email = self.get_input("Enter user email: ")

        # Verify email exists
        self.print_info("Checking if user exists...")
        check_sql = f"SELECT email, mfaEnabled FROM user WHERE email = '{user_email}';"
        result = self.run_db_query(check_sql, show_error_details=False)

        if not result:
            self.print_error(f"User not found: {user_email}")
            input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")
            return

        parts = result.split('|')
        if len(parts) >= 2:
            email = parts[0]
            mfa_enabled = parts[1]

            if mfa_enabled == "0":
                self.print_warning(f"2FA is already disabled for: {email}")
                if not self.confirm("Continue anyway?"):
                    return

        # Confirm
        print(f"\n{Colors.YELLOW}Warning: This will disable 2FA for:{Colors.END}")
        print(f"  Email: {user_email}")
        print()

        if not self.confirm("Proceed with disabling 2FA?"):
            self.print_info("Operation cancelled")
            input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")
            return

        # Disable 2FA
        self.print_info("Disabling 2FA...")
        disable_cmd = f"kubectl exec -it {self.pod_name} -n {self.workspace} -c n8n -- n8n mfa:disable --email={user_email}"
        result = self.run_command(disable_cmd, capture_output=True)

        if result and "Successfully disabled" in result:
            self.print_success(f"2FA disabled for: {user_email}")

            # Show cloudbot notification command
            print(f"\n{Colors.BOLD}Next step:{Colors.END}")
            print(f"Run this command in Slack to notify the user:")
            print(f"  {Colors.CYAN}/cloudbot notify [user_id] disable-2fa [thread_id]{Colors.END}")
        else:
            self.print_error("Failed to disable 2FA")
            if result:
                print(f"\n{Colors.RED}Output:{Colors.END}")
                print(result)

        input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")

    # ============================================================
    # Feature 4: Change Owner Email
    # ============================================================

    def change_owner_email(self):
        """Change workspace owner email"""
        self.print_header("Change Owner Email")

        # Important warnings
        print(f"{Colors.YELLOW}IMPORTANT CHECKS (you must verify):{Colors.END}")
        print("  □ Verified identity via ownership verification KB")
        print("  □ Checked mission control - new email doesn't own another instance")
        print("  □ 2FA not enabled (or disabled first)")
        print()

        if not self.confirm("Have you completed all verification checks?"):
            self.print_warning("Please complete verification checks before proceeding")
            input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")
            return

        # Get current owner
        self.print_info("Fetching current owner...")
        current_sql = "SELECT id, email, firstName, lastName FROM user WHERE roleSlug = 'global:owner';"
        result = self.run_db_query(current_sql)

        if not result:
            self.print_error("Could not find current owner")
            input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")
            return

        parts = result.split('|')
        if len(parts) >= 2:
            owner_id = parts[0]
            current_email = parts[1]
            print(f"\n{Colors.BOLD}Current owner:{Colors.END} {current_email}")
            print()
        else:
            self.print_error("Could not parse owner information")
            input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")
            return

        # Get new email
        new_email = self.get_input("Enter new owner email: ")

        # Check if new email already exists
        self.print_info("Checking if new email exists in workspace...")
        check_sql = f"SELECT email, roleSlug FROM user WHERE email = '{new_email}';"
        existing = self.run_db_query(check_sql, show_error_details=False)

        if existing:
            parts = existing.split('|')
            existing_email = parts[0]
            existing_role = parts[1] if len(parts) > 1 else "unknown"

            self.print_warning(f"Email already exists: {existing_email} ({existing_role})")
            print()
            print(f"{Colors.YELLOW}Options:{Colors.END}")
            print(f"  1. Use plus addressing (e.g., {new_email.split('@')[0]}+owner@{new_email.split('@')[1]})")
            print(f"  2. Continue anyway (will need to handle conflict)")
            print(f"  3. Cancel")
            print()

            choice = self.get_input("Select option (1/2/3): ")

            if choice == "1":
                # Suggest plus addressing
                username = new_email.split('@')[0]
                domain = new_email.split('@')[1]
                new_email = f"{username}+owner@{domain}"
                self.print_info(f"Using: {new_email}")
            elif choice == "2":
                self.print_warning("You will need to handle the existing user account")
            elif choice == "3":
                self.print_info("Operation cancelled")
                input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")
                return
            else:
                self.print_error("Invalid choice")
                input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")
                return

        # Final confirmation
        print(f"\n{Colors.YELLOW}Confirm owner email change:{Colors.END}")
        print(f"  Old: {current_email}")
        print(f"  New: {new_email}")
        print()

        confirm_text = self.get_input("Type 'CONFIRM' to proceed: ")
        if confirm_text != "CONFIRM":
            self.print_info("Operation cancelled")
            input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")
            return

        # Take backup first
        self.print_info("Taking backup first...")
        backup_cmd = f"kubectl exec -it {self.pod_name} -n {self.workspace} -c backup-cron -- n8n-backup.py backup"
        self.run_command(backup_cmd, capture_output=False)

        # Update owner email
        self.print_info("Updating owner email...")
        update_sql = f"UPDATE user SET email = '{new_email}' WHERE roleSlug = 'global:owner';"
        db_cmd = f"kubectl exec -it {self.pod_name} -n {self.workspace} -c backup-cron -- sqlite3 database.sqlite \"{update_sql}\""
        result = self.run_command(db_cmd, capture_output=True)

        # Verify change
        self.print_info("Verifying change...")
        verify_sql = "SELECT email FROM user WHERE roleSlug = 'global:owner';"
        verify_result = self.run_db_query(verify_sql)

        if verify_result and new_email in verify_result:
            self.print_success(f"Owner email updated successfully!")
            print()
            print(f"{Colors.BOLD}Important notes:{Colors.END}")
            print(f"  • New owner must use 'Forgot Password' to set password")
            print(f"  • Redeploy instance for changes to take effect")
            print()
            print(f"{Colors.BOLD}Next step:{Colors.END}")
            print(f"Run this command in Slack:")
            print(f"  {Colors.CYAN}/cloudbot redeploy-instance {self.workspace}{Colors.END}")
        else:
            self.print_error("Failed to update owner email")
            print("Verify the change manually or restore from backup")

        input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")

    # ============================================================
    # Original Features (v1.0/v1.1)
    # ============================================================

    def export_workflows(self):
        """Export workflows from live instance"""
        self.print_header("Export Workflows (Live Instance)")

        # Bug Fix #2: Check if pod is available
        if not self.pod_name:
            self.print_error("No pod available. Cannot export from live instance.")
            input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")
            return

        timestamp = datetime.now().strftime("%Y-%m-%d")
        filename = f"{self.workspace}-workflows-{timestamp}.json.gz"
        filepath = self.downloads_dir / filename

        self.print_info("Exporting workflows...")
        cmd = f"kubectl exec -it {self.pod_name} -n {self.workspace} -c n8n -- n8n export:workflow --pretty --all 2>&1 | gzip > {filepath}"

        result = self.run_command(cmd, capture_output=False, check=False)

        # Bug Fix #2: Validate result
        if filepath.exists() and filepath.stat().st_size > 0:
            # Check if the file contains error messages
            check_cmd = f"gzip -cd {filepath} 2>&1 | head -n 5"
            result_output = self.run_command(check_cmd, capture_output=True, check=False)

            if result_output and "Error from server" not in result_output and "error" not in result_output.lower():
                self.print_success(f"Workflows exported to: {filepath}")
                self.print_info(f"Extract with: gzip -d {filename}")
            else:
                self.print_error("Export failed - namespace not found or pod not accessible")
                if filepath.exists():
                    filepath.unlink()
        else:
            self.print_error("Export failed")
            if filepath.exists():
                filepath.unlink()

        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

    def export_from_backup(self):
        """Export workflows using workflow-exporter service"""
        self.print_header("Export Workflows (From Backup)")

        # Switch to services cluster
        self.print_info("Switching to services-gwc-1...")
        self.run_command("kubectx services-gwc-1")

        # List backups - capture output to check for errors and get latest
        self.print_info("Listing available backups...")
        list_cmd = f"kubectl exec --context services-gwc-1 -n workflow-exporter -i deploy/workflow-exporter -- pnpm wf {self.workspace} list"
        list_result = self.run_command(list_cmd, capture_output=True, check=False)

        # Fix 2: Check for errors in list command
        if list_result is None or "ERROR" in str(list_result) or "ContainerNotFound" in str(list_result):
            self.print_error(f"No backups found for '{self.workspace}'")
            self.print_info("Backups are retained for 90 days after deletion.")
            # Switch back to original cluster
            self.run_command(f"kubectx {self.cluster}")
            input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")
            return

        # Parse backup list
        import re
        backup_lines = [line.strip() for line in list_result.strip().split('\n') if line.strip() and '_sqldump_' in line]

        # Fix 2: Check if backup list is empty
        if not backup_lines:
            self.print_error(f"No backups found for '{self.workspace}'")
            self.print_info("Backups are retained for 90 days after deletion.")
            # Switch back to original cluster
            self.run_command(f"kubectx {self.cluster}")
            input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")
            return

        # Display the list to user
        print()
        print(list_result)
        print()

        # Ask which backup to use
        backup_name = self.get_input("Enter backup name (or press Enter for latest): ", required=False)

        # Fix 1: If no backup name provided, use latest (first in list)
        if not backup_name:
            backup_name = backup_lines[0]  # First item = newest backup

        # Export
        self.print_info("Exporting workflows...")
        if backup_name:
            export_cmd = f"kubectl exec --context services-gwc-1 -n workflow-exporter -i deploy/workflow-exporter -- pnpm wf {self.workspace} export {backup_name}"
        else:
            export_cmd = f"kubectl exec --context services-gwc-1 -n workflow-exporter -i deploy/workflow-exporter -- pnpm wf {self.workspace} export"

        self.run_command(export_cmd, capture_output=False)

        # Download
        self.print_info("Downloading archive...")

        # Fix 1: Parse date from backup name (works for both user-selected and latest)
        date_match = re.search(r'_sqldump_(\d{8})_', backup_name)
        if date_match:
            backup_date = date_match.group(1)  # e.g., "20251124"
        else:
            # Fallback if parsing fails
            backup_date = datetime.now().strftime("%Y%m%d")

        filename = f"{self.workspace}-workflows-backup-{backup_date}.zip"
        filepath = self.downloads_dir / filename

        download_cmd = f"kubectl exec --context services-gwc-1 -n workflow-exporter -i deploy/workflow-exporter -- cat /tmp/output/{self.workspace}-workflows.zip > {filepath}"
        result = self.run_command(download_cmd, capture_output=False)

        # Fix 3: Validate download wasn't empty
        if filepath.exists() and filepath.stat().st_size > 0:
            file_size = filepath.stat().st_size / 1024
            self.print_success(f"Workflows downloaded to: {filepath}")
            self.print_info(f"File size: {file_size:.1f} KB")
        else:
            self.print_error("Download failed")
            if filepath.exists():
                filepath.unlink()  # Clean up empty file

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

    # ============================================================
    # Feature: Pre-Menu and Deleted Instance Recovery
    # ============================================================

    def show_pre_menu(self):
        """Show pre-menu for operation mode selection"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'═' * 60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'SUPPORT MEDIC ASSISTANT v1.4':^60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'═' * 60}{Colors.END}\n")

        print(f"{Colors.BOLD}Select operation mode:{Colors.END}\n")
        print(f"{Colors.GREEN}1.{Colors.END} Full medic operations (live instance)")
        print(f"{Colors.GREEN}2.{Colors.END} Recover workflows from deleted instance")
        print()

        choice = self.get_input("Select option: ")
        return choice

    def setup_deleted_instance(self):
        """Setup for deleted instance recovery mode"""
        self.print_header("Deleted Instance Recovery - Setup")

        # VPN reminder
        self.print_warning("REMINDER: Make sure you're connected to the VPN!")
        print()

        # Get instance name only (no cluster needed)
        self.workspace = self.get_input("Enter instance name: ")
        self.deleted_instance_mode = True
        self.pod_name = None  # No pod for deleted instances
        self.cluster = None
        self.cluster_number = None

        return True

    def show_deleted_instance_menu(self):
        """Show deleted instance recovery menu"""
        while True:
            self.print_header("Deleted Instance Recovery")
            print(f"{Colors.BOLD}Instance:{Colors.END} {self.workspace}\n")

            menu_options = [
                ("1", "List available backups", self.list_deleted_instance_backups),
                ("2", "Export workflows (latest backup)", self.export_deleted_instance_latest),
                ("3", "Export workflows (select backup)", self.export_deleted_instance_specific),
                ("4", "Back to start", None)
            ]

            for key, description, _ in menu_options:
                print(f"{Colors.GREEN}{key}.{Colors.END} {description}")

            print()
            choice = self.get_input("Select option: ", required=False)

            if choice == '4':
                return False  # Go back to pre-menu

            # Find and execute the selected option
            for key, _, func in menu_options:
                if choice == key:
                    if func:
                        func()
                    break

    def list_deleted_instance_backups(self):
        """List available backups for deleted instance"""
        self.print_header("Available Backups")

        # Switch to services cluster
        self.print_info("Connecting to backup service...")
        switch_result = self.run_command("kubectx services-gwc-1", capture_output=True)

        if switch_result is None:
            self.print_error("Cannot connect to services-gwc-1. Check VPN and cluster access.")
            input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")
            return

        # List backups
        self.print_info(f"Listing backups for '{self.workspace}'...")
        print()

        list_cmd = f"kubectl exec --context services-gwc-1 -n workflow-exporter -i deploy/workflow-exporter -- pnpm wf {self.workspace} list"
        result = self.run_command(list_cmd, capture_output=True, check=False)

        # Check for errors or empty result
        if result is None or "ERROR" in str(result) or "Error" in str(result) or "ContainerNotFound" in str(result):
            self.print_error(f"No backups found for '{self.workspace}'. Backups are retained for 90 days after deletion.")
        else:
            print(result)
            self.print_info("Backups are retained for 90 days after deletion.")

        input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")

    def export_deleted_instance_latest(self):
        """Export workflows from latest backup of deleted instance"""
        self.print_header("Export Workflows (Latest Backup)")

        # Switch to services cluster
        self.print_info("Connecting to backup service...")
        switch_result = self.run_command("kubectx services-gwc-1", capture_output=True)

        if switch_result is None:
            self.print_error("Cannot connect to services-gwc-1. Check VPN and cluster access.")
            input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")
            return

        # First, list backups to get the latest backup name and date
        list_cmd = f"kubectl exec --context services-gwc-1 -n workflow-exporter -i deploy/workflow-exporter -- pnpm wf {self.workspace} list"
        list_result = self.run_command(list_cmd, capture_output=True, check=False)

        # Check for errors in list command
        if list_result is None or "ERROR" in str(list_result) or "Error" in str(list_result) or "ContainerNotFound" in str(list_result):
            self.print_error(f"No backups found for '{self.workspace}'.")
            self.print_info("Backups are retained for 90 days after deletion.")
            input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")
            return

        # Parse the latest backup name from list output
        # The list output contains backup filenames, one per line
        # Format: {instance}_sqldump_{YYYYMMDD}_{HHMM}.tar
        # Note: workflow-exporter returns backups sorted newest-first
        backup_lines = [line.strip() for line in list_result.strip().split('\n') if line.strip() and '_sqldump_' in line]

        if not backup_lines:
            self.print_error(f"No backups found for '{self.workspace}'.")
            self.print_info("Backups are retained for 90 days after deletion.")
            input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")
            return

        # The list is sorted newest-first, so first item = latest backup
        latest_backup = backup_lines[0]

        # Extract date from backup filename
        import re
        date_match = re.search(r'_sqldump_(\d{8})_', latest_backup)
        if date_match:
            backup_date = date_match.group(1)  # e.g., "20251113"
        else:
            # Fallback to today's date if parsing fails
            backup_date = datetime.now().strftime("%Y%m%d")

        # Export from latest backup
        self.print_info(f"Exporting workflows from latest backup...")
        export_cmd = f"kubectl exec --context services-gwc-1 -n workflow-exporter -i deploy/workflow-exporter -- pnpm wf {self.workspace} export"
        export_result = self.run_command(export_cmd, capture_output=True, check=False)

        # Check for errors in export command
        if export_result is None or "ERROR" in str(export_result) or "Error" in str(export_result):
            self.print_error(f"Export failed. No backups found for '{self.workspace}'.")
            self.print_info("Backups are retained for 90 days after deletion.")
            input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")
            return

        # Download the zip file with backup date
        self.print_info("Downloading workflows...")
        filename = f"{self.workspace}-workflows-backup-{backup_date}.zip"
        filepath = self.downloads_dir / filename

        download_cmd = f"kubectl exec --context services-gwc-1 -n workflow-exporter -i deploy/workflow-exporter -- cat /tmp/output/{self.workspace}-workflows.zip > {filepath}"
        download_result = self.run_command(download_cmd, capture_output=False, check=False)

        if filepath.exists() and filepath.stat().st_size > 0:
            file_size = filepath.stat().st_size / 1024
            self.print_success(f"Workflows exported to: {filepath}")
            self.print_info(f"File size: {file_size:.1f} KB")
        else:
            self.print_error("Download failed")
            if filepath.exists():
                filepath.unlink()

        input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")

    def export_deleted_instance_specific(self):
        """Export workflows from specific backup of deleted instance"""
        self.print_header("Export Workflows (Select Backup)")

        # Switch to services cluster
        self.print_info("Connecting to backup service...")
        switch_result = self.run_command("kubectx services-gwc-1", capture_output=True)

        if switch_result is None:
            self.print_error("Cannot connect to services-gwc-1. Check VPN and cluster access.")
            input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")
            return

        # List backups first
        self.print_info(f"Available backups for '{self.workspace}':")
        print()

        list_cmd = f"kubectl exec --context services-gwc-1 -n workflow-exporter -i deploy/workflow-exporter -- pnpm wf {self.workspace} list"
        list_result = self.run_command(list_cmd, capture_output=True, check=False)

        # Check for errors in list command
        if list_result is None or "ERROR" in str(list_result) or "Error" in str(list_result) or "ContainerNotFound" in str(list_result):
            self.print_error(f"No backups found for '{self.workspace}'. Backups are retained for 90 days after deletion.")
            input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")
            return

        print(list_result)
        print()

        # Get backup name
        backup_name = self.get_input("Enter backup name: ")

        # Export from specific backup
        self.print_info(f"Exporting workflows from backup '{backup_name}'...")
        export_cmd = f"kubectl exec --context services-gwc-1 -n workflow-exporter -i deploy/workflow-exporter -- pnpm wf {self.workspace} export {backup_name}"
        export_result = self.run_command(export_cmd, capture_output=True, check=False)

        # Check for errors in export command
        if export_result is None or "ERROR" in str(export_result) or "Error" in str(export_result):
            self.print_error(f"Export failed. Check backup name.")
            input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")
            return

        # Download the zip file
        self.print_info("Downloading workflows...")

        # Extract date from backup filename
        # Format: {instance}_sqldump_{YYYYMMDD}_{HHMM}.tar
        import re
        date_match = re.search(r'_sqldump_(\d{8})_', backup_name)
        if date_match:
            backup_date = date_match.group(1)  # e.g., "20251113"
        else:
            # Fallback if parsing fails
            backup_date = datetime.now().strftime("%Y%m%d")

        filename = f"{self.workspace}-workflows-backup-{backup_date}.zip"
        filepath = self.downloads_dir / filename

        download_cmd = f"kubectl exec --context services-gwc-1 -n workflow-exporter -i deploy/workflow-exporter -- cat /tmp/output/{self.workspace}-workflows.zip > {filepath}"
        download_result = self.run_command(download_cmd, capture_output=False, check=False)

        if filepath.exists() and filepath.stat().st_size > 0:
            file_size = filepath.stat().st_size / 1024
            self.print_success(f"Workflows exported to: {filepath}")
            self.print_info(f"File size: {file_size:.1f} KB")
        else:
            self.print_error("Download failed")
            if filepath.exists():
                filepath.unlink()

        input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")

    def run(self):
        """Main application loop"""
        try:
            while True:
                # Show pre-menu
                choice = self.show_pre_menu()

                if choice == '1':
                    # Full medic operations (existing flow)
                    if not self.setup_workspace():
                        continue

                    # Main loop
                    while True:
                        if not self.show_main_menu():
                            break

                elif choice == '2':
                    # Deleted instance recovery
                    if not self.setup_deleted_instance():
                        continue

                    # Deleted instance menu loop
                    if self.show_deleted_instance_menu() == False:
                        # User chose to go back
                        self.deleted_instance_mode = False
                        continue

                else:
                    self.print_error("Invalid option. Please select 1 or 2.")
                    continue

                # Ask if user wants to continue or quit
                if not self.confirm("\nPerform another operation?"):
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
