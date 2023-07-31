"""
Create wind speed and direction plot for last 24 and 48 hours from ncas-radar-wind-profiler-1

"""


from netCDF4 import Dataset
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import datetime as dt
import os


#################################
# Options to potentially change #
#################################

deployment='20230710_woest'
nc_file_path = f'/gws/pw/j07/ncas_obs_vol1/amf/processing/ncas-radar-wind-profiler-1/{deployment}'
plots_path = '/gws/pw/j07/woest/public/quicklooks/ncas-radar-wind-profiler-1'
mode = 'low'

#################################


def create_time_xaxis(sampling_interval, days=1):
    """
    Creates x axis of time for last n days.

    Args:
        sampling_interval (int): Number of minutes between data files
        days (int): Number of days for x axis

    Returns:
        array: timestamps
    """
    current_time = dt.datetime.now(dt.timezone.utc)
    latest_sample_time = int((current_time.hour * 60 + current_time.minute) / sampling_interval) * sampling_interval
    latest_sample_hour = int(latest_sample_time / 60)
    latest_sample_minute = latest_sample_time - (latest_sample_hour * 60)

    latest_sample_time_data = f"{current_time.year}{zero_pad_number(current_time.month)}{zero_pad_number(current_time.day)}T{zero_pad_number(latest_sample_hour)}{zero_pad_number(latest_sample_minute)}+0000"
    time_format = "%Y%m%dT%H%M%z"
    latest_sample_dttime = dt.datetime.strptime(latest_sample_time_data,time_format)
    y_dttime = latest_sample_dttime - dt.timedelta(days=days)

    x_time = np.array(range(int(y_dttime.timestamp()), int(latest_sample_dttime.timestamp())+1, sampling_interval*60))

    return x_time
    
    
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



def add_text(ax,plt,text,xpos=0.0,ypos=1.01,fontsize=12,color='black'):
    plt.text(xpos,ypos,text,fontsize=fontsize, transform=ax.transAxes, color=color)



def simple_2d_plot(variable, ncfile, save_loc, cmap='viridis', zero_centre_cbar = False):
    """
    Creates plot of variable for today from ncas-radar-wind-profiler-1
    
    Args:
        variable (str): Name of variable in netCDF file
        ncfile (str): File path and name of netCDF file with today's data.
        save_loc (str): File path to save plots to.
        cmap (str): Optional. Name of colour map to use in plot. Default 'viridis'
        zero_centre_cbar (bool): Optional. Color bar centred around 0 (true) or not (false). Default 'False'.
    
    """

    nc = Dataset(ncfile)

    x_time = nc['time'][:]
    x_time = [dt.datetime.utcfromtimestamp(time) for time in x_time]
    
    y_altitude = nc['altitude'][:]
    
    data = nc[variable][:]
    
    x,y = np.meshgrid(x_time,y_altitude)
#    vmax = np.nanpercentile(np.abs(data.compressed()),98) if zero_centre_cbar else None
#    vmin = -np.nanpercentile(np.abs(data.compressed()),98) if zero_centre_cbar else None

    if variable == "upward_wind":
        vmin = -2
        vmax = 2
    elif "signal_to_noise" in variable:
        vmin = 0
        vmax = 45
    else:
        vmax = np.nanpercentile(np.abs(data.compressed()),98) if zero_centre_cbar else None
        vmin = -np.nanpercentile(np.abs(data.compressed()),98) if zero_centre_cbar else None
    
    fig = plt.figure(figsize=(20,8))
    fig.set_facecolor('white')
    ax = fig.add_subplot(111)
    
    pc = ax.pcolormesh(x,y,data.T,cmap=cmap,vmin=vmin,vmax=vmax)
    plt.gca().xaxis.set_minor_locator(mdates.HourLocator(byhour=range(0,24,2)))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M\n%Y/%m/%d"))
    ax.set_ylabel('Altitude (m)', fontsize=17)
    ax.set_xlabel('Time (UTC)', fontsize=17)
    ax.set_title(f'{variable} - {dt.datetime.now().year}-{zero_pad_number(dt.datetime.now().month)}-{zero_pad_number(dt.datetime.now().day)}', fontsize=19)
    #ax.set_title(f'{variable} - 2023-07-31', fontsize=19)
    ax.tick_params(axis='both', which='both', labelsize=14)
    ax.grid(which='both')
    

    cbar = fig.colorbar(pc, ax = ax)
    cbar.ax.set_ylabel(f'{variable} ({nc[variable].units})', fontsize=17)
    cbar.ax.tick_params(axis='both', which='both', labelsize=12)

    #add_text(ax,plt,'NCAS Radar Wind Profiler 1\nCapel Dewi Atmospheric Observatory, Wales, UK')
    plt.tight_layout()
    if "signal_to_noise_ratio" in variable:
        plt.savefig(f'{save_loc}/snr.png')
    elif "upward_air_velocity" in variable:
        plt.savefig(f'{save_loc}/upward_wind.png')
    else:
        plt.savefig(f'{save_loc}/{variable.lower()}.png')
    plt.close()




def wind_speed_direction_plot(ncfile, save_loc, barb_interval=3):
    """
    Creates wind speed and direction plot for today from ncas-radar-wind-profiler-1
    
    Args:
        ncfile (str): File path and name of netCDF file with today's data.
        save_loc (str): File path to save plots to.
        barb_interval (int): Optional. Interval between data points to plot wind barbs. Default is 3.
    
    """
    
    nc = Dataset(ncfile)

    x_time = nc['time'][:]
    x_time = [dt.datetime.utcfromtimestamp(time) for time in x_time]
    
    y_altitude = nc['altitude'][:]
    
    data_ws = nc['wind_speed'][:]
    data_dir = nc['wind_from_direction'][:]
                    
    # get u and v wind components
    u = data_ws * -np.sin(np.deg2rad(data_dir))
    v = data_ws * -np.cos(np.deg2rad(data_dir))

    
    # make and save plot
    x,y = np.meshgrid(x_time,y_altitude)
    
    fig = plt.figure(figsize=(20,8))
    fig.set_facecolor('white')
    ax = fig.add_subplot(111)
    
    pc = ax.pcolormesh(x,y,data_ws.T,vmin=0,vmax=25)
    plt.gca().xaxis.set_minor_locator(mdates.HourLocator(byhour=range(0,24,2)))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M\n%Y/%m/%d"))
    ax.set_ylabel('Altitude (m)', fontsize=17)
    ax.set_xlabel('Time (UTC)', fontsize=17)
    ax.set_title(f'Wind speed and direction - {dt.datetime.now().year}-{zero_pad_number(dt.datetime.now().month)}-{zero_pad_number(dt.datetime.now().day)}', fontsize=19)
    #ax.set_title(f'Wind speed and direction - 2023-07-31', fontsize=19)
    ax.tick_params(axis='both', which='both', labelsize=14)
    ax.grid(which='both')    

    cbar = fig.colorbar(pc, ax = ax)
    cbar.ax.set_ylabel('Wind speed (m/s)', fontsize=17)
    cbar.ax.tick_params(axis='both', which='both', labelsize=12)
    
    #ax.barbs(x[::barb_interval,::barb_interval], y[::barb_interval,::barb_interval], u[::barb_interval,::barb_interval].T, v[::barb_interval,::barb_interval].T, length = 6)
    # want all arrows to be same length
    arrow_length = 1
    v1 = (((arrow_length ** 2) / ((u**2 / v**2) + 1)) ** 0.5) * np.sign(v)
    u1 = (v1/v)*u 

    ax.quiver(x[::barb_interval,::barb_interval], y[::barb_interval,::barb_interval], u1[::barb_interval,::barb_interval].T, v1[::barb_interval,::barb_interval].T, scale=48, scale_units='width')

    #add_text(ax,plt,'NCAS Radar Wind Profiler 1\nCapel Dewi Atmospheric Observatory, Wales, UK') 

    plt.tight_layout()
    plt.savefig(f'{save_loc}/horizontal_winds.png')
    #plt.savefig(f'{save_loc}/winds.pdf')
    plt.close()



def main(nc_file_path=nc_file_path, plots_path=plots_path, mode=mode):
    """
    Make plots for last 24/48 hours of wind profiler data.
    
    Args:
        nc_file_path (str): Location of netCDF files
        plots_path (str): Location to save plots.
        mode (str): Operation mode of wind profiler (high or low).
    
    """
    plots_path = f'{plots_path}/{dt.datetime.now().year}-{zero_pad_number(dt.datetime.now().month)}-{zero_pad_number(dt.datetime.now().day)}'
    #plots_path = f'{plots_path}/2023-07-31'
    
    if not os.path.exists(f'{plots_path}/{mode}min'):
        os.makedirs(f'{plots_path}/{mode}min')
    
    today_date = dt.datetime.now()
    #today_date = dt.datetime.strptime("2023-07-31","%Y-%m-%d")
    today_nc_file_path=f'{nc_file_path}/{today_date.year}/{zero_pad_number(today_date.month)}'
    
    today_file = f'ncas-radar-wind-profiler-1_mobile_{today_date.year}{zero_pad_number(today_date.month)}{zero_pad_number(today_date.day)}_snr-winds_{mode}min_v1.0.nc'
    
    if os.path.exists(f'{today_nc_file_path}/{today_file}'):
        wind_speed_direction_plot(f'{today_nc_file_path}/{today_file}', f'{plots_path}/{mode}min')

        for var in ['upward_air_velocity']:   
            simple_2d_plot(var, f'{today_nc_file_path}/{today_file}', f'{plots_path}/{mode}min', cmap='RdBu_r', zero_centre_cbar=True) 

        for var in ['signal_to_noise_ratio_minimum']:
            simple_2d_plot(var, f'{today_nc_file_path}/{today_file}', f'{plots_path}/{mode}min')



if __name__ == "__main__":
    main(mode="5")
    main(mode="15")
