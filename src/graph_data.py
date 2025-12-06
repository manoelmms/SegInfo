# Receive csv data from server to analyze performance using TLS vs non-TLS (TCP)
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def load_performance_data(file_path):
    try:
        data = pd.read_csv(file_path, names=['timestamp', 'connection_type', 'data_size', 'duration'])
        data['data_size'] = data['data_size'].astype(int)
        data['duration'] = data['duration'].astype(float)
        # Convert to MB
        data['data_size_mb'] = data['data_size'] / (1024 * 1024)
        # Convert duration to milliseconds
        data['duration_ms'] = data['duration'] * 1000
        # Calculate speed in MB/s
        data['speed_mbps'] = data['data_size_mb'] / data['duration']
        return data
    except Exception as e:
        print(f"Error loading performance data from {file_path}: {e}")
        return None
    
def analyze_performance(data):
    if data is None or data.empty:
        print("No data to analyze.")
        return

    summary = data.groupby('connection_type').agg(
        total_data_size_mb=pd.NamedAgg(column='data_size_mb', aggfunc='sum'),
        total_duration_s=pd.NamedAgg(column='duration', aggfunc='sum'),
        average_speed_mbps=pd.NamedAgg(column='speed_mbps', aggfunc='mean')
    ).reset_index()

    print("\n" + "="*60)
    print("Performance Summary:")
    print("="*60)
    print(summary)
    
    # Calculate TLS overhead
    if 'TLS' in summary['connection_type'].values and 'TCP' in summary['connection_type'].values:
        tls_speed = summary[summary['connection_type'] == 'TLS']['average_speed_mbps'].values[0]
        tcp_speed = summary[summary['connection_type'] == 'TCP']['average_speed_mbps'].values[0]
        
        overhead_pct = ((tcp_speed - tls_speed) / tcp_speed) * 100
        
        print("\n" + "="*60)
        print("TLS Performance Impact:")
        print("="*60)
        print(f"TCP Average Speed:  {tcp_speed:.2f} MB/s")
        print(f"TLS Average Speed:  {tls_speed:.2f} MB/s")
        print(f"Speed Difference:   {tcp_speed - tls_speed:.2f} MB/s")
        print(f"TLS Overhead:       {overhead_pct:.2f}%")
        print("="*60)
    print()

def create_graph(data):
    if data is None or data.empty:
        print("No data to create graph.")
        return

    # Separate data by connection type
    tls_data = data[data['connection_type'] == 'TLS'].sort_values('data_size_mb')
    tcp_data = data[data['connection_type'] == 'TCP'].sort_values('data_size_mb')

    # Create individual graphs
    create_time_graph(tls_data, tcp_data)
    create_speed_graph(tls_data, tcp_data)
    create_comparison_graph(tls_data, tcp_data)
    
    print("\nAll graphs saved successfully!")

def create_time_graph(tls_data, tcp_data):
    """Graph 1: Transfer Time Comparison"""
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    # TLS Time
    if not tls_data.empty:
        grouped_tls = tls_data.groupby('data_size_mb').agg({
            'duration_ms': ['mean', 'std']
        }).reset_index()
        grouped_tls.columns = ['data_size_mb', 'mean', 'std']
        
        axes[0].plot(grouped_tls['data_size_mb'], grouped_tls['mean'], 
                     marker='o', color='#2E86AB', linewidth=2, markersize=8)
        axes[0].fill_between(grouped_tls['data_size_mb'], 
                             grouped_tls['mean'] - grouped_tls['std'], 
                             grouped_tls['mean'] + grouped_tls['std'],
                             alpha=0.3, color='#2E86AB')
        axes[0].set_xlabel('File Size (MB)', fontsize=11)
        axes[0].set_ylabel('Transfer Time (milliseconds)', fontsize=11)
        axes[0].set_title('TLS Transfer Time', fontsize=13, fontweight='bold')
        axes[0].set_xticks(grouped_tls['data_size_mb'])
        axes[0].set_xticklabels([f'{int(x)}' for x in grouped_tls['data_size_mb']])
    else:
        axes[0].text(0.5, 0.5, 'No TLS data available', 
                     ha='center', va='center', transform=axes[0].transAxes)
    
    # TCP Time
    if not tcp_data.empty:
        grouped_tcp = tcp_data.groupby('data_size_mb').agg({
            'duration_ms': ['mean', 'std']
        }).reset_index()
        grouped_tcp.columns = ['data_size_mb', 'mean', 'std']
        
        axes[1].plot(grouped_tcp['data_size_mb'], grouped_tcp['mean'], 
                     marker='s', color='#A23B72', linewidth=2, markersize=8)
        axes[1].fill_between(grouped_tcp['data_size_mb'], 
                             grouped_tcp['mean'] - grouped_tcp['std'], 
                             grouped_tcp['mean'] + grouped_tcp['std'],
                             alpha=0.3, color='#A23B72')
        axes[1].set_xlabel('File Size (MB)', fontsize=11)
        axes[1].set_ylabel('Transfer Time (milliseconds)', fontsize=11)
        axes[1].set_title('TCP Transfer Time', fontsize=13, fontweight='bold')
        axes[1].set_xticks(grouped_tcp['data_size_mb'])
        axes[1].set_xticklabels([f'{int(x)}' for x in grouped_tcp['data_size_mb']])
    else:
        axes[1].text(0.5, 0.5, 'No TCP data available', 
                     ha='center', va='center', transform=axes[1].transAxes)
    
    # Comparison
    if not tls_data.empty and not tcp_data.empty:
        grouped_tls = tls_data.groupby('data_size_mb').agg({
            'duration_ms': ['mean', 'std']
        }).reset_index()
        grouped_tls.columns = ['data_size_mb', 'mean_tls', 'std_tls']
        
        grouped_tcp = tcp_data.groupby('data_size_mb').agg({
            'duration_ms': ['mean', 'std']
        }).reset_index()
        grouped_tcp.columns = ['data_size_mb', 'mean_tcp', 'std_tcp']
        
        axes[2].plot(grouped_tls['data_size_mb'], grouped_tls['mean_tls'], 
                     marker='o', label='TLS', color='#2E86AB', linewidth=2, markersize=8)
        axes[2].fill_between(grouped_tls['data_size_mb'], 
                             grouped_tls['mean_tls'] - grouped_tls['std_tls'], 
                             grouped_tls['mean_tls'] + grouped_tls['std_tls'],
                             alpha=0.2, color='#2E86AB')
        
        axes[2].plot(grouped_tcp['data_size_mb'], grouped_tcp['mean_tcp'], 
                     marker='s', label='TCP', color='#A23B72', linewidth=2, markersize=8)
        axes[2].fill_between(grouped_tcp['data_size_mb'], 
                             grouped_tcp['mean_tcp'] - grouped_tcp['std_tcp'], 
                             grouped_tcp['mean_tcp'] + grouped_tcp['std_tcp'],
                             alpha=0.2, color='#A23B72')
        axes[2].legend(fontsize=11)
    elif not tls_data.empty:
        grouped_tls = tls_data.groupby('data_size_mb').agg({
            'duration_ms': ['mean', 'std']
        }).reset_index()
        grouped_tls.columns = ['data_size_mb', 'mean', 'std']
        
        axes[2].plot(grouped_tls['data_size_mb'], grouped_tls['mean'], 
                     marker='o', label='TLS', color='#2E86AB', linewidth=2, markersize=8)
        axes[2].fill_between(grouped_tls['data_size_mb'], 
                             grouped_tls['mean'] - grouped_tls['std'], 
                             grouped_tls['mean'] + grouped_tls['std'],
                             alpha=0.3, color='#2E86AB')
        axes[2].legend(fontsize=11)
    elif not tcp_data.empty:
        grouped_tcp = tcp_data.groupby('data_size_mb').agg({
            'duration_ms': ['mean', 'std']
        }).reset_index()
        grouped_tcp.columns = ['data_size_mb', 'mean', 'std']
        
        axes[2].plot(grouped_tcp['data_size_mb'], grouped_tcp['mean'], 
                     marker='s', label='TCP', color='#A23B72', linewidth=2, markersize=8)
        axes[2].fill_between(grouped_tcp['data_size_mb'], 
                             grouped_tcp['mean'] - grouped_tcp['std'], 
                             grouped_tcp['mean'] + grouped_tcp['std'],
                             alpha=0.3, color='#A23B72')
        axes[2].legend(fontsize=11)
    
    axes[2].set_xlabel('File Size (MB)', fontsize=11)
    axes[2].set_ylabel('Transfer Time (milliseconds)', fontsize=11)
    axes[2].set_title('TLS vs TCP - Transfer Time', fontsize=13, fontweight='bold')
    if not tls_data.empty:
        sizes = sorted(tls_data['data_size_mb'].unique())
        axes[2].set_xticks(sizes)
        axes[2].set_xticklabels([f'{int(x)}' for x in sizes])
    
    plt.tight_layout()
    plt.savefig('graph_transfer_time.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: graph_transfer_time.png")

def create_speed_graph(tls_data, tcp_data):
    """Graph 2: Transfer Speed Comparison"""
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    # TLS Speed
    if not tls_data.empty:
        grouped_tls = tls_data.groupby('data_size_mb').agg({
            'speed_mbps': ['mean', 'std']
        }).reset_index()
        grouped_tls.columns = ['data_size_mb', 'mean', 'std']
        
        axes[0].plot(grouped_tls['data_size_mb'], grouped_tls['mean'], 
                     marker='o', color='#2E86AB', linewidth=2, markersize=8)
        axes[0].fill_between(grouped_tls['data_size_mb'], 
                             grouped_tls['mean'] - grouped_tls['std'], 
                             grouped_tls['mean'] + grouped_tls['std'],
                             alpha=0.3, color='#2E86AB')
        axes[0].set_xlabel('File Size (MB)', fontsize=11)
        axes[0].set_ylabel('Transfer Speed (MB/s)', fontsize=11)
        axes[0].set_title('TLS Transfer Speed', fontsize=13, fontweight='bold')
        axes[0].set_xticks(grouped_tls['data_size_mb'])
        axes[0].set_xticklabels([f'{int(x)}' for x in grouped_tls['data_size_mb']])
    else:
        axes[0].text(0.5, 0.5, 'No TLS data available', 
                     ha='center', va='center', transform=axes[0].transAxes)
    
    # TCP Speed
    if not tcp_data.empty:
        grouped_tcp = tcp_data.groupby('data_size_mb').agg({
            'speed_mbps': ['mean', 'std']
        }).reset_index()
        grouped_tcp.columns = ['data_size_mb', 'mean', 'std']
        
        axes[1].plot(grouped_tcp['data_size_mb'], grouped_tcp['mean'], 
                     marker='s', color='#A23B72', linewidth=2, markersize=8)
        axes[1].fill_between(grouped_tcp['data_size_mb'], 
                             grouped_tcp['mean'] - grouped_tcp['std'], 
                             grouped_tcp['mean'] + grouped_tcp['std'],
                             alpha=0.3, color='#A23B72')
        axes[1].set_xlabel('File Size (MB)', fontsize=11)
        axes[1].set_ylabel('Transfer Speed (MB/s)', fontsize=11)
        axes[1].set_title('TCP Transfer Speed', fontsize=13, fontweight='bold')
        axes[1].set_xticks(grouped_tcp['data_size_mb'])
        axes[1].set_xticklabels([f'{int(x)}' for x in grouped_tcp['data_size_mb']])
    else:
        axes[1].text(0.5, 0.5, 'No TCP data available', 
                     ha='center', va='center', transform=axes[1].transAxes)
    
    # Comparison
    if not tls_data.empty and not tcp_data.empty:
        grouped_tls = tls_data.groupby('data_size_mb').agg({
            'speed_mbps': ['mean', 'std']
        }).reset_index()
        grouped_tls.columns = ['data_size_mb', 'mean_tls', 'std_tls']
        
        grouped_tcp = tcp_data.groupby('data_size_mb').agg({
            'speed_mbps': ['mean', 'std']
        }).reset_index()
        grouped_tcp.columns = ['data_size_mb', 'mean_tcp', 'std_tcp']
        
        axes[2].plot(grouped_tls['data_size_mb'], grouped_tls['mean_tls'], 
                     marker='o', label='TLS', color='#2E86AB', linewidth=2, markersize=8)
        axes[2].fill_between(grouped_tls['data_size_mb'], 
                             grouped_tls['mean_tls'] - grouped_tls['std_tls'], 
                             grouped_tls['mean_tls'] + grouped_tls['std_tls'],
                             alpha=0.2, color='#2E86AB')
        
        axes[2].plot(grouped_tcp['data_size_mb'], grouped_tcp['mean_tcp'], 
                     marker='s', label='TCP', color='#A23B72', linewidth=2, markersize=8)
        axes[2].fill_between(grouped_tcp['data_size_mb'], 
                             grouped_tcp['mean_tcp'] - grouped_tcp['std_tcp'], 
                             grouped_tcp['mean_tcp'] + grouped_tcp['std_tcp'],
                             alpha=0.2, color='#A23B72')
        axes[2].legend(fontsize=11)
    elif not tls_data.empty:
        grouped_tls = tls_data.groupby('data_size_mb').agg({
            'speed_mbps': ['mean', 'std']
        }).reset_index()
        grouped_tls.columns = ['data_size_mb', 'mean', 'std']
        
        axes[2].plot(grouped_tls['data_size_mb'], grouped_tls['mean'], 
                     marker='o', label='TLS', color='#2E86AB', linewidth=2, markersize=8)
        axes[2].fill_between(grouped_tls['data_size_mb'], 
                             grouped_tls['mean'] - grouped_tls['std'], 
                             grouped_tls['mean'] + grouped_tls['std'],
                             alpha=0.3, color='#2E86AB')
        axes[2].legend(fontsize=11)
    elif not tcp_data.empty:
        grouped_tcp = tcp_data.groupby('data_size_mb').agg({
            'speed_mbps': ['mean', 'std']
        }).reset_index()
        grouped_tcp.columns = ['data_size_mb', 'mean', 'std']
        
        axes[2].plot(grouped_tcp['data_size_mb'], grouped_tcp['mean'], 
                     marker='s', label='TCP', color='#A23B72', linewidth=2, markersize=8)
        axes[2].fill_between(grouped_tcp['data_size_mb'], 
                             grouped_tcp['mean'] - grouped_tcp['std'], 
                             grouped_tcp['mean'] + grouped_tcp['std'],
                             alpha=0.3, color='#A23B72')
        axes[2].legend(fontsize=11)
    
    axes[2].set_xlabel('File Size (MB)', fontsize=11)
    axes[2].set_ylabel('Transfer Speed (MB/s)', fontsize=11)
    axes[2].set_title('TLS vs TCP - Transfer Speed', fontsize=13, fontweight='bold')
    if not tls_data.empty:
        sizes = sorted(tls_data['data_size_mb'].unique())
        axes[2].set_xticks(sizes)
        axes[2].set_xticklabels([f'{int(x)}' for x in sizes])
    
    plt.tight_layout()
    plt.savefig('graph_transfer_speed.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: graph_transfer_speed.png")

def create_comparison_graph(tls_data, tcp_data):
    """Graph 3: Performance Comparison Overview"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Bar chart: Average Speed
    if not tls_data.empty or not tcp_data.empty:
        speeds = []
        labels = []
        colors = []
        
        if not tls_data.empty:
            speeds.append(tls_data['speed_mbps'].mean())
            labels.append('TLS')
            colors.append('#2E86AB')
        
        if not tcp_data.empty:
            speeds.append(tcp_data['speed_mbps'].mean())
            labels.append('TCP')
            colors.append('#A23B72')
        
        axes[0].bar(labels, speeds, color=colors, alpha=0.8, width=0.6)
        axes[0].set_ylabel('Average Speed (MB/s)', fontsize=11)
        axes[0].set_title('Average Transfer Speed Comparison', fontsize=13, fontweight='bold')
        
        # Add value labels on bars
        for i, v in enumerate(speeds):
            axes[0].text(i, v + max(speeds)*0.02, f'{v:.2f}', 
                        ha='center', va='bottom', fontweight='bold')
    
    # Performance overhead percentage
    if not tls_data.empty and not tcp_data.empty:
        # Calculate overhead for each file size
        grouped_tcp = tcp_data.groupby('data_size_mb')['duration_ms'].mean().reset_index()
        grouped_tcp.columns = ['data_size_mb', 'duration_tcp']
        
        grouped_tls = tls_data.groupby('data_size_mb')['duration_ms'].mean().reset_index()
        grouped_tls.columns = ['data_size_mb', 'duration_tls']
        
        merged = grouped_tcp.merge(grouped_tls, on='data_size_mb')
        merged['overhead_pct'] = ((merged['duration_tls'] - merged['duration_tcp']) / 
                                  merged['duration_tcp'] * 100)
        
        axes[1].plot(merged['data_size_mb'], merged['overhead_pct'], 
                    marker='D', color='#F18F01', linewidth=2, markersize=8)
        axes[1].axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        axes[1].set_xlabel('File Size (MB)', fontsize=11)
        axes[1].set_ylabel('TLS Overhead (%)', fontsize=11)
        axes[1].set_title('TLS Performance Overhead', fontsize=13, fontweight='bold')
        axes[1].set_xticks(merged['data_size_mb'])
        axes[1].set_xticklabels([f'{int(x)}' for x in merged['data_size_mb']])
    else:
        axes[1].text(0.5, 0.5, 'Need both TLS and TCP data', 
                    ha='center', va='center', transform=axes[1].transAxes)
    
    plt.tight_layout()
    plt.savefig('graph_performance_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: graph_performance_comparison.png")

if __name__ == "__main__":
    performance_data = load_performance_data('client_performance.log')
    analyze_performance(performance_data)
    create_graph(performance_data)
    print("Performance analysis and graph generation completed.")
