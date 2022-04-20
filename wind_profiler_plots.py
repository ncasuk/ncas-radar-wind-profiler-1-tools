"""
Create wind speed and direction plot for last 24 and 48 hours from ncas-radar-wind-profiler-1

"""


from netCDF4 import Dataset
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sys
import numpy as np
import datetime as dt



#################################
# Options to potentially change #
#################################

nc_file_path = '/gws/nopw/j04/ncas_obs/cdao/processing/ncas-radar-wind-profiler-1/netcdf_files'
plots_path = '/gws/nopw/j04/ncas_obs/cdao/public/ncas-radar-wind-profiler-1'
mode = 'low'

#################################



def wind_speed_direction_plot_last24(yesterday_ncfile, today_ncfile, save_loc, barb_interval=3):
    """
    Creates wind speed and direction plot for last 24 hours from ncas-radar-wind-profiler-1
    
    Args:
        yesterday_ncfile (str): File path and name of netCDF file with yesterday's data.
        today_ncfile (str): File path and name of netCDF file with today's data.
        save_loc (str): File path to save plots to.
        barb_interval (int): Optional. Interval between data points to plot wind barbs. Default is 3.
    
    """
    
    if 'low-mode' in yesterday_ncfile:
        mode = 'low'
    else:
        mode = 'high'
    
    yesterday_ncfile = Dataset(yesterday_ncfile)
    today_ncfile = Dataset(today_ncfile)
    
    # create x axis of all sampling times in last 24 hours
    # sampling_interval attribute in file should be something like '15 mintues'
    sampling_interval = int(today_ncfile.sampling_interval.split(' ')[0])
    
    current_time = dt.datetime.now()
    latest_sample_time = int((current_time.hour * 60 + current_time.minute) / sampling_interval) * sampling_interval
    latest_sample_hour = int(latest_sample_time / 60)
    latest_sample_minute = latest_sample_time - (latest_sample_hour * 60)
    
    latest_sample_time_data = f"{current_time.year}{current_time.month}{current_time.day}T{latest_sample_hour}{latest_sample_minute}"
    time_format = "%Y%m%dT%H%M"
    latest_sample_dttime = dt.datetime.strptime(latest_sample_time_data,time_format)
    y_dttime = latest_sample_dttime - dt.timedelta(days=1)
    
    x_time = np.array(range(int(y_dttime.timestamp()), int(latest_sample_dttime.timestamp())+1, sampling_interval*60))
    
    # get y axis data
    if 'altitude' in yesterday_ncfile.dimensions.keys() and 'altitude' in today_ncfile.dimensions.keys():
        y_altitude = yesterday_ncfile['altitude'][:]
        altitude_label = 'Altitude (m)'
    else:
        y_altitude = range(yesterday_ncfile['altitude'][:].shape[1])
        altitude_label = 'Index'
    
    # make empty arrays to fill with data
    data_ws = np.ma.ones((len(x_time),len(y_altitude))) * -99999
    data_ws = np.ma.masked_where(data_ws == -99999, data_ws)
    data_dir = np.ma.ones((len(x_time),len(y_altitude))) * -99999
    data_dir = np.ma.masked_where(data_dir == -99999, data_dir)
    
    # fill the arrays with data from the right time when there is data at that time
    for i, time in enumerate(x_time):
        found = False
        for j, yt in enumerate(yesterday_ncfile['time'][:]):
            if int(yt) == time:
                data_ws[i] = yesterday_ncfile['wind_speed'][j]
                data_dir[i] = yesterday_ncfile['wind_from_direction'][j]
                found = True
        if not found:
            for j, tt in enumerate(today_ncfile['time'][:]):
                if int(tt) == time:
                    data_ws[i] = today_ncfile['wind_speed'][j]
                    data_dir[i] = today_ncfile['wind_from_direction'][j]
                    

    # get u and v wind components
    u = data_ws * np.sin(np.deg2rad(data_dir))
    v = data_ws * np.cos(np.deg2rad(data_dir))

    # convert x time units back into datetime format
    x_time = [dt.datetime.fromtimestamp(time) for time in x_time]
    
    # make and save plot
    x,y = np.meshgrid(x_time,y_altitude)
    
    fig = plt.figure(figsize=(40,16))
    fig.set_facecolor('white')
    ax = fig.add_subplot(111)
    
    pc = ax.pcolormesh(x,y,data_ws.T)
    plt.gca().xaxis.set_minor_locator(mdates.HourLocator(byhour=range(0,24,2)))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M\n%Y/%m/%d"))
    ax.set_ylabel(altitude_label, fontsize=28)
    ax.set_xlabel('Time', fontsize=28)
    ax.set_title('Last 24 hours', fontsize=32)
    ax.tick_params(axis='both', which='both', labelsize=24)
    
    cbar = fig.colorbar(pc, ax = ax)
    cbar.ax.set_ylabel('Wind speed (m/s)', fontsize=28)
    cbar.ax.tick_params(axis='both', which='both', labelsize=20)
    
    ax.barbs(x[::barb_interval,::barb_interval], y[::barb_interval,::barb_interval], u[::barb_interval,::barb_interval].T, v[::barb_interval,::barb_interval].T, length = 10)
    
    plt.tight_layout()
    plt.savefig(f'{save_loc}/ncas-wind-profiler-1_{mode}-mode_wind-speed-direction_last-24-hours.png')
    plt.savefig(f'{save_loc}/ncas-wind-profiler-1_{mode}-mode_wind-speed-direction_last-24-hours.pdf')
    plt.close()



def wind_speed_direction_plot_last48(day_before_yesterday_ncfile, yesterday_ncfile, today_ncfile, save_loc, barb_interval=3):
    """
    Creates wind speed and direction plot for last 48 hours from ncas-radar-wind-profiler-1
    
    Args:
        day_before_yesterday_ncfile (str): File path and name of netCDF file for the day before yesterday.
        yesterday_ncfile (str): File path and name of netCDF file with yesterday's data.
        today_ncfile (str): File path and name of netCDF file with today's data.
        save_loc (str): File path to save plots to.
        barb_interval (int): Optional. Interval between data points to plot wind barbs. Default is 3.
    
    """
    
    if 'low-mode' in yesterday_ncfile:
        mode = 'low'
    else:
        mode = 'high'
    
    day_before_yesterday_ncfile = Dataset(day_before_yesterday_ncfile)
    yesterday_ncfile = Dataset(yesterday_ncfile)
    today_ncfile = Dataset(today_ncfile)
    
    # create x axis of all sampling times in last 24 hours
    # sampling_interval attribute in file should be something like '15 mintues'
    sampling_interval = int(today_ncfile.sampling_interval.split(' ')[0])
    
    current_time = dt.datetime.now()
    latest_sample_time = int((current_time.hour * 60 + current_time.minute) / sampling_interval) * sampling_interval
    latest_sample_hour = int(latest_sample_time / 60)
    latest_sample_minute = latest_sample_time - (latest_sample_hour * 60)
    
    latest_sample_time_data = f"{current_time.year}{current_time.month}{current_time.day}T{latest_sample_hour}{latest_sample_minute}"
    time_format = "%Y%m%dT%H%M"
    latest_sample_dttime = dt.datetime.strptime(latest_sample_time_data,time_format)
    y_dttime = latest_sample_dttime - dt.timedelta(days=2)
    
    x_time = np.array(range(int(y_dttime.timestamp()), int(latest_sample_dttime.timestamp())+1, sampling_interval*60))
    
    # get y axis data
    if 'altitude' in yesterday_ncfile.dimensions.keys() and 'altitude' in today_ncfile.dimensions.keys() and 'altitude' in day_before_yesterday_ncfile.dimensions.keys():
        y_altitude = yesterday_ncfile['altitude'][:]
        altitude_label = 'Altitude (m)'
    else:
        y_altitude = range(yesterday_ncfile['altitude'][:].shape[1])
        altitude_label = 'Index'
    
    # make empty arrays to fill with data
    data_ws = np.ma.ones((len(x_time),len(y_altitude))) * -99999
    data_ws = np.ma.masked_where(data_ws == -99999, data_ws)
    data_dir = np.ma.ones((len(x_time),len(y_altitude))) * -99999
    data_dir = np.ma.masked_where(data_dir == -99999, data_dir)
    
    # fill the arrays with data from the right time when there is data at that time
    for i, time in enumerate(x_time):
        found = False
        for j, dbt in enumerate(day_before_yesterday_ncfile['time'][:]):
            if int(dbt) == time:
                data_ws[i] = day_before_yesterday_ncfile['wind_speed'][j]
                data_dir[i] = day_before_yesterday_ncfile['wind_from_direction'][j]
                found = True
        if not found:
            for j, yt in enumerate(yesterday_ncfile['time'][:]):
                if int(yt) == time:
                    data_ws[i] = yesterday_ncfile['wind_speed'][j]
                    data_dir[i] = yesterday_ncfile['wind_from_direction'][j]
                    found = True
        if not found:
            for j, tt in enumerate(today_ncfile['time'][:]):
                if int(tt) == time:
                    data_ws[i] = today_ncfile['wind_speed'][j]
                    data_dir[i] = today_ncfile['wind_from_direction'][j]
                    

    # get u and v wind components
    u = data_ws * np.sin(np.deg2rad(data_dir))
    v = data_ws * np.cos(np.deg2rad(data_dir))

    # convert x time units back into datetime format
    x_time = [dt.datetime.fromtimestamp(time) for time in x_time]
    
    # make and save plot
    x,y = np.meshgrid(x_time,y_altitude)
    
    fig = plt.figure(figsize=(40,16))
    fig.set_facecolor('white')
    ax = fig.add_subplot(111)
    
    pc = ax.pcolormesh(x,y,data_ws.T)
    plt.gca().xaxis.set_minor_locator(mdates.HourLocator(byhour=range(0,24,2)))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M\n%Y/%m/%d"))
    ax.set_ylabel(altitude_label, fontsize=28)
    ax.set_xlabel('Time', fontsize=28)
    ax.set_title('Last 48 hours', fontsize=32)
    ax.tick_params(axis='both', which='both', labelsize=24)
    
    cbar = fig.colorbar(pc, ax = ax)
    cbar.ax.set_ylabel('Wind speed (m/s)', fontsize=28)
    cbar.ax.tick_params(axis='both', which='both', labelsize=20)
    
    ax.barbs(x[::barb_interval,::barb_interval], y[::barb_interval,::barb_interval], u[::barb_interval,::barb_interval].T, v[::barb_interval,::barb_interval].T, length = 10)
    
    plt.tight_layout()
    plt.savefig(f'{save_loc}/ncas-wind-profiler-1_{mode}-mode_wind-speed-direction_last-48-hours.png')
    plt.savefig(f'{save_loc}/ncas-wind-profiler-1_{mode}-mode_wind-speed-direction_last-48-hours.pdf')
    plt.close()
    
    
    
def zero_pad_number(n):
    """
    Returns single digit number n as '0n'
    Returns multiple digit number n as 'n'
    Used for date or month strings
    
    Args:
        n (int): Number
        
    Returns:
        str: Number with zero padding if single digit.
        
    """
    if len(f'{n}') == 1:
        return f'0{n}'
    else:
        return f'{n}'
    
    
    
def main(nc_file_path=nc_file_path, plots_path=plots_path, mode=mode):
    """
    Make plots for last 24/48 hours of wind profiler data.
    
    Args:
        nc_file_path (str): Location of netCDF files
        plots_path (str): Location to save plots.
        mode (str): Operation mode of wind profiler (high or low).
    
    """
    today_date = dt.datetime.now()
    yesterday_date = today_date - dt.timedelta(days=1)
    day_before_yesterday_date = today_date - dt.timedelta(days=2)
    
    today_file = f'ncas-radar-wind-profiler-1_cdao_{today_date.year}{zero_pad_number(today_date.month)}{zero_pad_number(today_date.day)}_snr-winds_{mode}-mode_15min_v1.0.nc'
    
    yesterday_file = f'ncas-radar-wind-profiler-1_cdao_{yesterday_date.year}{zero_pad_number(yesterday_date.month)}{zero_pad_number(yesterday_date.day)}_snr-winds_{mode}-mode_15min_v1.0.nc'
    
    day_before_yesterday_file = f'ncas-radar-wind-profiler-1_cdao_{day_before_yesterday_date.year}{zero_pad_number(day_before_yesterday_date.month)}{zero_pad_number(day_before_yesterday_date.day)}_snr-winds_{mode}-mode_15min_v1.0.nc'
    
    
    wind_speed_direction_plot_last24(f'{nc_file_path}/{yesterday_file}', f'{nc_file_path}/{today_file}', plots_path)
    
    wind_speed_direction_plot_last48(f'{nc_file_path}/{day_before_yesterday_file}',f'{nc_file_path}/{yesterday_file}', f'{nc_file_path}/{today_file}', plots_path)
    
    


if __name__ == "__main__":
    #yesterday_ncfile = sys.argv[1]
    #today_ncfile = sys.argv[2]
    #save_loc = sys.argv[3]
    #barb_interval = 3
    #wind_speed_direction_plot_last24(yesterday_ncfile=yesterday_ncfile, today_ncfile=today_ncfile, save_loc=save_loc, barb_interval=barb_interval)
    main(mode="low")
    main(mode="high")