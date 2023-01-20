import pandas as pd
import concurrent.futures
import nbimporter
from allocation_strategies import (AllocationManager, run_through_time)


# Creates instance and gets results
def create_allocation(allocated_capital, allocation_periods, frequency,
                      start_date, upfront_percent, risk_free_rate):
    sim_alloc = AllocationManager()
    sim_alloc.capital = allocated_capital
    sim_alloc.allocation_periods = allocation_periods
    sim_alloc.frequency = frequency
    sim_alloc.start_date = start_date
    sim_alloc.upfront_percent = upfront_percent
    sim_alloc.risk_free_rate = risk_free_rate
    sim_alloc.allocate_capital()
    print("Running Allocation Manager for:")
    print(sim_alloc.__dict__)
    # Run this allocation through time
    _, stats = run_through_time(sim_alloc)
    return (stats['inputs'] | stats['outputs'])


# Runs scenarios in threads to make it quicker
def run_simulations(sim_allocated_capital, sim_start_date, sim_risk_free_rate,
                    sim_frequencies, sim_upfront_percents,
                    sim_allocation_periods):
    alloc_list = []

    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = [
            executor.submit(create_allocation, sim_allocated_capital,
                            allocation, freq, sim_start_date, upfront,
                            sim_risk_free_rate) for freq in sim_frequencies
            for upfront in sim_upfront_percents
            for allocation in sim_allocation_periods[freq]
        ]

        for f in concurrent.futures.as_completed(results):
            a = f.result()
            alloc_list.append(a)

    sim_df = pd.DataFrame(alloc_list)
    return (sim_df)
