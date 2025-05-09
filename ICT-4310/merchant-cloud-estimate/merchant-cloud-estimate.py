class AzureCostEstimator:
    """
    Estimates Azure monthly and multi-year cloud costs using verified pricing.
    Incorporates:
    - VMs (D-series)
    - SQL storage and I/O
    - Blob storage
    - Reserved network egress
    - Azure Functions (On-Demand, with free tier logic)
    - assumes 50000 transactions
    - assumes b2ps vs Vm from azure
    """

    def __init__(self,
                 vm_count=8,
                 vm_monthly_rate=49.0560,
                 sql_storage_gb=8000 * 1 / 1024,      # 1 KB per transaction
                 sql_rate_per_gb=0.25,
                 sql_read_ops=50000,                   # 1 read per transaction
                 sql_write_ops=50000,                  # 1 write per transaction
                 sql_read_rate_per_10k=0.019,
                 sql_write_rate_per_10k=0.0228,
                 blob_storage_gb=100,
                 blob_rate_per_gb=0.15,
                 egress_tb_reserved=1,
                 egress_100tb_rate=1545.0,
                 function_exec_count=8000,            # 1 function exec per transaction
                 function_gb_seconds=8000 * 0.5,       # 0.5 GB-s per execution
                 function_exec_price_per_million=0.40,
                 function_gb_second_rate=0.000026):

        self.vm_count = vm_count
        self.vm_monthly_rate = vm_monthly_rate
        self.sql_storage_gb = sql_storage_gb
        self.sql_rate_per_gb = sql_rate_per_gb
        self.sql_read_ops = sql_read_ops
        self.sql_write_ops = sql_write_ops
        self.sql_read_rate_per_10k = sql_read_rate_per_10k
        self.sql_write_rate_per_10k = sql_write_rate_per_10k
        self.blob_storage_gb = blob_storage_gb
        self.blob_rate_per_gb = blob_rate_per_gb
        self.egress_tb_reserved = egress_tb_reserved
        self.egress_100tb_rate = egress_100tb_rate
        self.function_exec_count = function_exec_count
        self.function_gb_seconds = function_gb_seconds
        self.function_exec_price_per_million = function_exec_price_per_million
        self.function_gb_second_rate = function_gb_second_rate

    def compute_vm_cost(self):
        return self.vm_count * self.vm_monthly_rate

    def compute_sql_storage_cost(self):
        return self.sql_storage_gb * self.sql_rate_per_gb

    def compute_sql_ops_cost(self):
        reads = (self.sql_read_ops / 10000) * self.sql_read_rate_per_10k
        writes = (self.sql_write_ops / 10000) * self.sql_write_rate_per_10k
        return reads + writes

    def compute_blob_storage_cost(self):
        return self.blob_storage_gb * self.blob_rate_per_gb

    def compute_egress_cost(self):
        return (self.egress_tb_reserved / 100) * self.egress_100tb_rate

    def compute_function_cost(self):
        # Free tier: 1M executions and 400,000 GB-s/month
        billable_execs = max(0, self.function_exec_count - 1_000_000)
        billable_gb_s = max(0, self.function_gb_seconds - 400_000)

        exec_cost = (billable_execs / 1_000_000) * self.function_exec_price_per_million
        gb_s_cost = billable_gb_s * self.function_gb_second_rate

        return exec_cost + gb_s_cost

    def total_monthly_cost(self):
        return (
            self.compute_vm_cost() +
            self.compute_sql_storage_cost() +
            self.compute_sql_ops_cost() +
            self.compute_blob_storage_cost() +
            self.compute_egress_cost() +
            self.compute_function_cost()
        )

    def projected_cost(self, years):
        return self.total_monthly_cost() * 12 * years

    def breakdown(self):
        return {
            "VMs": self.compute_vm_cost(),
            "SQL Storage": self.compute_sql_storage_cost(),
            "SQL Operations": self.compute_sql_ops_cost(),
            "Blob Storage": self.compute_blob_storage_cost(),
            "Network Egress (Reserved)": self.compute_egress_cost(),
            "Azure Functions (On-Demand)": self.compute_function_cost(),
            "Total Monthly": self.total_monthly_cost(),
            "2-Year Total": self.projected_cost(2),
            "5-Year Total": self.projected_cost(5),
        }


# === Example Execution ===
if __name__ == "__main__":
    estimator = AzureCostEstimator()
    results = estimator.breakdown()
    for item, cost in results.items():
        print(f"{item:<35}: ${cost:,.2f}")