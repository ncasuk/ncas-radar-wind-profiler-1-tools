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

nc_file_path = '/gws/pw/j07/ncas_obs_vol1/cdao/processing/ncas-radar-wind-profiler-1/netcdf_files'
plots_path = '/gws/pw/j07/ncas_obs_vol1/cdao/public/ncas-radar-wind-profiler-1'
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



def add_text(ax,plt,text,xpos=0.0,ypos=1.01,fontsize=12,color='black'):
    plt.text(xpos,ypos,text,fontsize=fontsize, transform=ax.transAxes, color=color)



def simple_2d_plot_last24(variable, yesterday_ncfile, today_ncfile, save_loc, cmap='viridis', zero_centre_cbar = False):
    if 'low-mode' in yesterday_ncfile:
        mode = 'low'
    else:
        mode = 'high'

    if os.path.exists(yesterday_ncfile):
        yesterday_exists = True 
        yesterday_ncfile = Dataset(yesterday_ncfile)
        ncfile = yesterday_ncfile
    else:
        yesterday_exists = False

    if os.path.exists(today_ncfile):
        today_exists = True
        today_ncfile = Dataset(today_ncfile)
        ncfile = today_ncfile
    else:
        today_exists = False


    # if any files exist, get data
    # if no file exists, make empty plot
    if today_exists or yesterday_exists:
        # create x axis of all sampling times in last 24 hours
        # sampling_interval attribute in file should be something like '15 mintues'
        sampling_interval = int(ncfile.sampling_interval.split(' ')[0])
    
        x_time = create_time_xaxis(sampling_interval)
    
        # get y axis data
        y_altitude = ncfile['altitude'][:]

        # empty array for data to add to
        data = np.ma.ones((len(x_time),len(y_altitude))) * -99999
        data = np.ma.masked_where(data == -99999, data)
    
        # fill the arrays with data from the right time when there is data at that time
        for i, time in enumerate(x_time):
            found = False
            if yesterday_exists:
                for j, yt in enumerate(yesterday_ncfile['time'][:]):
                    if int(yt) == time:
                        data[i] = yesterday_ncfile[variable][j]
                        found = True
            if not found and today_exists:
                for j, tt in enumerate(today_ncfile['time'][:]):
                    if int(tt) == time:
                        data[i] = today_ncfile[variable][j]
    
        # convert x time units back into datetime format
        x_time = [dt.datetime.utcfromtimestamp(time) for time in x_time]

    else:
        # data for empty plot
        x_time = create_time_xaxis(15)
        x_time = [dt.datetime.utcfromtimestamp(time) for time in x_time]
        y_altitude = np.linspace(0,8000,9)
        data = np.ma.ones((len(x_time),len(y_altitude))) * -99999
        data = np.ma.masked_where(data == -99999, data)


    # make and save plot
    x,y = np.meshgrid(x_time,y_altitude)

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
    ax.set_title('Last 24 hours', fontsize=19)
    ax.tick_params(axis='both', which='both', labelsize=14)
    ax.grid(which='both')

    cbar = fig.colorbar(pc, ax = ax)
    if yesterday_exists or today_exists:
        cbar.ax.set_ylabel(f'{variable} ({ncfile[variable].units})', fontsize=17)
    else:
        cbar.ax.set_ylabel(f'{variable}', fontsize=17)
    cbar.ax.tick_params(axis='both', which='both', labelsize=12)

    add_text(ax,plt,'NCAS Radar Wind Profiler 1\nCapel Dewi Atmospheric Observatory, Wales, UK')
    plt.tight_layout()
    plt.savefig(f'{save_loc}/ncas-wind-profiler-1_{mode}-mode_{variable.lower()}_last-24-hours.png')
    plt.savefig(f'{save_loc}/ncas-wind-profiler-1_{mode}-mode_{variable.lower()}_last-24-hours.pdf')
    plt.close()




def simple_2d_plot_last48(variable, day_before_yesterday_ncfile, yesterday_ncfile, today_ncfile, save_loc, cmap='viridis', zero_centre_cbar=False):
    if 'low-mode' in yesterday_ncfile:
        mode = 'low'
    else:
        mode = 'high'

    if os.path.exists(day_before_yesterday_ncfile):
        day_before_yesterday_exists = True
        day_before_yesterday_ncfile = Dataset(day_before_yesterday_ncfile)
        ncfile = day_before_yesterday_ncfile
    else:
        day_before_yesterday_exists = False

    if os.path.exists(yesterday_ncfile):
        yesterday_exists = True
        yesterday_ncfile = Dataset(yesterday_ncfile)
        ncfile = yesterday_ncfile
    else:
        yesterday_exists = False

    if os.path.exists(today_ncfile):
        today_exists = True
        today_ncfile = Dataset(today_ncfile)
        ncfile = today_ncfile
    else:
        today_exists = False


    # if any files exist, get data
    # if no file exists, make empty plot
    if today_exists or yesterday_exists or day_before_yesterday_exists:
        # create x axis of all sampling times in last 24 hours
        # sampling_interval attribute in file should be something like '15 mintues'
        sampling_interval = int(ncfile.sampling_interval.split(' ')[0])

        x_time = create_time_xaxis(sampling_interval, days = 2)

        # get y axis data
        y_altitude = ncfile['altitude'][:]

        # empty array for data to add to
        data = np.ma.ones((len(x_time),len(y_altitude))) * -99999
        data = np.ma.masked_where(data == -99999, data)

        # fill the arrays with data from the right time when there is data at that time
        for i, time in enumerate(x_time):
            found = False
            if day_before_yesterday_exists:
                for j, dbt in enumerate(day_before_yesterday_ncfile['time'][:]):
                    if int(dbt) == time:
                        data[i] = day_before_yesterday_ncfile[variable][j]
                        found = True
            if not found and yesterday_exists:
                for j, yt in enumerate(yesterday_ncfile['time'][:]):
                    if int(yt) == time:
                        data[i] = yesterday_ncfile[variable][j]
            if not found and today_exists:
                for j, tt in enumerate(today_ncfile['time'][:]):
                    if int(tt) == time:
                        data[i] = today_ncfile[variable][j]

        # convert x time units back into datetime format
        x_time = [dt.datetime.utcfromtimestamp(time) for time in x_time]

    else:
        # data for empty plot
        x_time = create_time_xaxis(15, days = 2)
        x_time = [dt.datetime.utcfromtimestamp(time) for time in x_time]
        y_altitude = np.linspace(0,8000,9)
        data = np.ma.ones((len(x_time),len(y_altitude))) * -99999
        data = np.ma.masked_where(data == -99999, data)


    # make and save plot
    x,y = np.meshgrid(x_time,y_altitude)

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
    ax.set_title('Last 48 hours', fontsize=19)
    ax.tick_params(axis='both', which='both', labelsize=14)
    ax.grid(which='both')

    cbar = fig.colorbar(pc, ax = ax)
    if yesterday_exists or today_exists:
        cbar.ax.set_ylabel(f'{variable} ({ncfile[variable].units})', fontsize=17)
    else:
        cbar.ax.set_ylabel(f'{variable}', fontsize=17)
    cbar.ax.tick_params(axis='both', which='both', labelsize=12)

    
    add_text(ax,plt,'NCAS Radar Wind Profiler 1\nCapel Dewi Atmospheric Observatory, Wales, UK')
    plt.tight_layout()
    plt.savefig(f'{save_loc}/ncas-wind-profiler-1_{mode}-mode_{variable.lower()}_last-48-hours.png')
    plt.savefig(f'{save_loc}/ncas-wind-profiler-1_{mode}-mode_{variable.lower()}_last-48-hours.pdf')
    plt.close()



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
    
    if os.path.exists(yesterday_ncfile):
        yesterday_exists = True
        yesterday_ncfile = Dataset(yesterday_ncfile)
        ncfile = yesterday_ncfile
    else:
        yesterday_exists = False

    if os.path.exists(today_ncfile):
        today_exists = True
        today_ncfile = Dataset(today_ncfile)
        ncfile = today_ncfile
    else:
        today_exists = False

    
    # if any files exist, get data
    # if no file exists, make empty plot
    if today_exists or yesterday_exists:
        # create x axis of all sampling times in last 24 hours
        # sampling_interval attribute in file should be something like '15 mintues'
        sampling_interval = int(ncfile.sampling_interval.split(' ')[0])
       
        x_time = create_time_xaxis(sampling_interval, days=1)
 
        # get y axis data
        y_altitude = ncfile['altitude'][:]
    
        # make empty arrays to fill with data
        data_ws = np.ma.ones((len(x_time),len(y_altitude))) * -99999
        data_ws = np.ma.masked_where(data_ws == -99999, data_ws)
        data_dir = np.ma.ones((len(x_time),len(y_altitude))) * -99999
        data_dir = np.ma.masked_where(data_dir == -99999, data_dir)
    
        # fill the arrays with data from the right time when there is data at that time
        for i, time in enumerate(x_time):
            found = False
            if yesterday_exists:
                for j, yt in enumerate(yesterday_ncfile['time'][:]):
                    if int(yt) == time:
                        data_ws[i] = yesterday_ncfile['wind_speed'][j]
                        data_dir[i] = yesterday_ncfile['wind_from_direction'][j]
                        found = True
            if not found and today_exists:
                for j, tt in enumerate(today_ncfile['time'][:]):
                    if int(tt) == time:
                        data_ws[i] = today_ncfile['wind_speed'][j]
                        data_dir[i] = today_ncfile['wind_from_direction'][j]
                    

        # get u and v wind components
        u = data_ws * -np.sin(np.deg2rad(data_dir))
        v = data_ws * -np.cos(np.deg2rad(data_dir))

        # convert x time units back into datetime format
        x_time = [dt.datetime.utcfromtimestamp(time) for time in x_time]
    else:
        # data for empty plot
        x_time = create_time_xaxis(15)
        x_time = [dt.datetime.utcfromtimestamp(time) for time in x_time]
        y_altitude = np.linspace(0,8000,9)
        data_ws = np.ma.ones((len(x_time),len(y_altitude))) * -99999
        data_ws = np.ma.masked_where(data_ws == -99999, data_ws)
        data_dir = np.ma.ones((len(x_time),len(y_altitude))) * -99999
        data_dir = np.ma.masked_where(data_dir == -99999, data_dir)
        u = data_ws * -np.sin(np.deg2rad(data_dir))
        v = data_ws * -np.cos(np.deg2rad(data_dir))

    
    # make and save plot
    x,y = np.meshgrid(x_time,y_altitude)
    
    fig = plt.figure(figsize=(20,8))
    fig.set_facecolor('white')
    ax = fig.add_subplot(111)
    
    pc = ax.pcolormesh(x,y,data_ws.T)
    plt.gca().xaxis.set_minor_locator(mdates.HourLocator(byhour=range(0,24,2)))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M\n%Y/%m/%d"))
    ax.set_ylabel('Altitude (m)', fontsize=17)
    ax.set_xlabel('Time (UTC)', fontsize=17)
    ax.set_title('Last 24 hours', fontsize=19)
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

    add_text(ax,plt,'NCAS Radar Wind Profiler 1\nCapel Dewi Atmospheric Observatory, Wales, UK') 

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
    
    if os.path.exists(day_before_yesterday_ncfile):
        day_before_yesterday_exists = True
        day_before_yesterday_ncfile = Dataset(day_before_yesterday_ncfile)
        ncfile = day_before_yesterday_ncfile
    else:
        day_before_yesterday_exists = False


    if os.path.exists(yesterday_ncfile):
        yesterday_exists = True
        yesterday_ncfile = Dataset(yesterday_ncfile)
        ncfile = yesterday_ncfile
    else:
        yesterday_exists = False

    if os.path.exists(today_ncfile):
        today_exists = True
        today_ncfile = Dataset(today_ncfile)
        ncfile = today_ncfile
    else:
        today_exists = False
    

    # if any files exist, get data
    # if no file exists, make empty plot
    if today_exists or yesterday_exists or day_before_yesterday_exists:    
        # create x axis of all sampling times in last 24 hours
        # sampling_interval attribute in file should be something like '15 mintues'
        sampling_interval = int(ncfile.sampling_interval.split(' ')[0])
        
        x_time = create_time_xaxis(sampling_interval, days=2)
 
        # get y axis data
        y_altitude = ncfile['altitude'][:]
 
        # make empty arrays to fill with data
        data_ws = np.ma.ones((len(x_time),len(y_altitude))) * -99999
        data_ws = np.ma.masked_where(data_ws == -99999, data_ws)
        data_dir = np.ma.ones((len(x_time),len(y_altitude))) * -99999
        data_dir = np.ma.masked_where(data_dir == -99999, data_dir)
        
        # fill the arrays with data from the right time when there is data at that time
        for i, time in enumerate(x_time):
            found = False
            if day_before_yesterday_exists:
                for j, dbt in enumerate(day_before_yesterday_ncfile['time'][:]):
                    if int(dbt) == time:
                        data_ws[i] = day_before_yesterday_ncfile['wind_speed'][j]
                        data_dir[i] = day_before_yesterday_ncfile['wind_from_direction'][j]
                        found = True
            if not found and yesterday_exists:
                for j, yt in enumerate(yesterday_ncfile['time'][:]):
                    if int(yt) == time:
                        data_ws[i] = yesterday_ncfile['wind_speed'][j]
                        data_dir[i] = yesterday_ncfile['wind_from_direction'][j]
                        found = True
            if not found and today_exists:
                for j, tt in enumerate(today_ncfile['time'][:]):
                    if int(tt) == time:
                        data_ws[i] = today_ncfile['wind_speed'][j]
                        data_dir[i] = today_ncfile['wind_from_direction'][j]
                    

        # get u and v wind components
        u = data_ws * -np.sin(np.deg2rad(data_dir))
        v = data_ws * -np.cos(np.deg2rad(data_dir))
    
        # convert x time units back into datetime format
        x_time = [dt.datetime.utcfromtimestamp(time) for time in x_time]
    else:
        # data for empty plot
        x_time = create_time_xaxis(15, days = 2)
        x_time = [dt.datetime.utcfromtimestamp(time) for time in x_time]
        y_altitude = np.linspace(0,8000,9)
        data_ws = np.ma.ones((len(x_time),len(y_altitude))) * -99999
        data_ws = np.ma.masked_where(data_ws == -99999, data_ws)
        data_dir = np.ma.ones((len(x_time),len(y_altitude))) * -99999
        data_dir = np.ma.masked_where(data_dir == -99999, data_dir)
        u = data_ws * -np.sin(np.deg2rad(data_dir))
        v = data_ws * -np.cos(np.deg2rad(data_dir))
    
    # make and save plot
    x,y = np.meshgrid(x_time,y_altitude)
    
    fig = plt.figure(figsize=(20,8))
    fig.set_facecolor('white')
    ax = fig.add_subplot(111)
    
    pc = ax.pcolormesh(x,y,data_ws.T)
    plt.gca().xaxis.set_minor_locator(mdates.HourLocator(byhour=range(0,24,2)))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M\n%Y/%m/%d"))
    ax.set_ylabel('Altitude (m)', fontsize=17)
    ax.set_xlabel('Time (UTC)', fontsize=17)
    ax.set_title('Last 48 hours', fontsize=19)
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


    add_text(ax,plt,'NCAS Radar Wind Profiler 1\nCapel Dewi Atmospheric Observatory, Wales, UK')    
    
    plt.tight_layout()
    plt.savefig(f'{save_loc}/ncas-wind-profiler-1_{mode}-mode_wind-speed-direction_last-48-hours.png')
    plt.savefig(f'{save_loc}/ncas-wind-profiler-1_{mode}-mode_wind-speed-direction_last-48-hours.pdf')
    plt.close()
    


def multi_plot_24hrs(variables, yesterday_ncfile, today_ncfile, save_loc):
    """
    variable - list
    """
    if 'low-mode' in yesterday_ncfile:
        mode = 'low'
    else:
        mode = 'high'

    if os.path.exists(yesterday_ncfile):
        yesterday_exists = True
        yesterday_ncfile = Dataset(yesterday_ncfile)
        ncfile = yesterday_ncfile
    else:
        yesterday_exists = False

    if os.path.exists(today_ncfile):
        today_exists = True
        today_ncfile = Dataset(today_ncfile)
        ncfile = today_ncfile
    else:
        today_exists = False


    # if any files exist, get data
    # if no file exists, make empty plot
    if today_exists or yesterday_exists:
        # create x axis of all sampling times in last 24 hours
        # sampling_interval attribute in file should be something like '15 mintues'
        sampling_interval = int(ncfile.sampling_interval.split(' ')[0])

        x_time1 = create_time_xaxis(sampling_interval, days=1)
        # convert x time units back into datetime format
        x_time = [dt.datetime.utcfromtimestamp(time) for time in x_time1]

        y_altitude = ncfile['altitude'][:]

        x,y = np.meshgrid(x_time,y_altitude)
    
        no_plots = len(variables)

        fig = plt.figure(figsize=(20,8*no_plots))
        fig.set_facecolor('white')
    
        for n in range(no_plots):
            variable = variables[n]
            ax = fig.add_subplot(no_plots,1,n+1)
             
            data = np.ma.ones((len(x_time),len(y_altitude))) * -99999
            data = np.ma.masked_where(data == -99999, data)
    
            for i, time in enumerate(x_time1):
                found = False
                if yesterday_exists:
                    for j, yt in enumerate(yesterday_ncfile['time'][:]):
                        if int(yt) == time:
                            data[i] = yesterday_ncfile[variable][j]
                            found = True
                if not found and today_exists:
                    for j, tt in enumerate(today_ncfile['time'][:]):
                        if int(tt) == time:
                            data[i] = today_ncfile[variable][j]
            
            pc = ax.pcolormesh(x,y,data.T)
            ax.xaxis.set_minor_locator(mdates.HourLocator(byhour=range(0,24,2)))
            ax.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
            ax.xaxis.set_major_locator(mdates.DayLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M\n%Y/%m/%d"))
            ax.set_ylabel('Altitude (m)', fontsize=17)
            ax.set_xlabel('Time (UTC)', fontsize=17)
            #ax.set_title('Last 24 hours', fontsize=19)
            ax.tick_params(axis='both', which='both', labelsize=14)
            ax.grid(axis='both', which='both')

            if n == 0:
                add_text(ax,plt,'NCAS Radar Wind Profiler 1\nCapel Dewi Atmospheric Observatory, Wales, UK')        

            cbar = fig.colorbar(pc, ax = ax)
            cbar.ax.set_ylabel(f'{variable} ({ncfile[variable].units})', fontsize=17)
            cbar.ax.tick_params(axis='both', which='both', labelsize=12)
    else:
        # data for empty plot
        x_time = create_time_xaxis(15)
        x_time = [dt.datetime.utcfromtimestamp(time) for time in x_time]
        y_altitude = np.linspace(0,8000,9)
        data = np.ma.ones((len(x_time),len(y_altitude))) * -99999
        data = np.ma.masked_where(data == -99999, data)
        x,y = np.meshgrid(x_time,y_altitude)
        no_plots = len(variables)
        fig = plt.figure(figsize=(20,8*no_plots))
        fig.set_facecolor('white')
        for n in range(no_plots):
            variable = variables[n]
            ax = fig.add_subplot(no_plots,1,n+1)
            pc = ax.pcolormesh(x,y,data.T)
            ax.xaxis.set_minor_locator(mdates.HourLocator(byhour=range(0,24,2)))
            ax.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
            ax.xaxis.set_major_locator(mdates.DayLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M\n%Y/%m/%d"))
            ax.set_ylabel('Altitude (m)', fontsize=17)
            ax.set_xlabel('Time (UTC)', fontsize=17)
            ax.tick_params(axis='both', which='both', labelsize=14)
            ax.grid(axis='both', which='both')

            if n == 0:
                add_text(ax,plt,'NCAS Radar Wind Profiler 1\nCapel Dewi Atmospheric Observatory, Wales, UK')

            cbar = fig.colorbar(pc, ax = ax)
            cbar.ax.set_ylabel(f'{variable}', fontsize=17)
            cbar.ax.tick_params(axis='both', which='both', labelsize=12)


    plt.tight_layout()
    plt.savefig(f'{save_loc}/ncas-wind-profiler-1_{mode}-mode_multipanel_last-24-hours.png')
    plt.savefig(f'{save_loc}/ncas-wind-profiler-1_{mode}-mode_multipanel_last-24-hours.pdf')
    plt.close()



def multi_plot_48hrs(variables, day_before_yesterday_ncfile, yesterday_ncfile, today_ncfile, save_loc):
    """
    variable - list
    """
    if 'low-mode' in yesterday_ncfile:
        mode = 'low'
    else:
        mode = 'high'

    if os.path.exists(day_before_yesterday_ncfile):
        day_before_yesterday_exists = True
        day_before_yesterday_ncfile = Dataset(day_before_yesterday_ncfile)
        ncfile = day_before_yesterday_ncfile
    else:
        day_before_yesterday_exists = False


    if os.path.exists(yesterday_ncfile):
        yesterday_exists = True
        yesterday_ncfile = Dataset(yesterday_ncfile)
        ncfile = yesterday_ncfile
    else:
        yesterday_exists = False

    if os.path.exists(today_ncfile):
        today_exists = True
        today_ncfile = Dataset(today_ncfile)
        ncfile = today_ncfile
    else:
        today_exists = False


    # if any files exist, get data
    # if no file exists, make empty plot
    if today_exists or yesterday_exists or day_before_yesterday_exists:
        # create x axis of all sampling times in last 24 hours
        # sampling_interval attribute in file should be something like '15 mintues'
        sampling_interval = int(ncfile.sampling_interval.split(' ')[0])


        x_time1 = create_time_xaxis(sampling_interval, days=2)
        # convert x time units back into datetime format
        x_time = [dt.datetime.utcfromtimestamp(time) for time in x_time1]

        y_altitude = ncfile['altitude'][:]

        x,y = np.meshgrid(x_time,y_altitude)

        no_plots = len(variables)
    
        fig = plt.figure(figsize=(20,8*no_plots))
        fig.set_facecolor('white')
    
        for n in range(no_plots):
            variable = variables[n]
            ax = fig.add_subplot(no_plots,1,n+1)
    
            data = np.ma.ones((len(x_time),len(y_altitude))) * -99999
            data = np.ma.masked_where(data == -99999, data)
    
            for i, time in enumerate(x_time1):
                found = False
                if day_before_yesterday_exists:
                    for j, dbt in enumerate(day_before_yesterday_ncfile['time'][:]):
                        if int(dbt) == time:
                            data[i] = day_before_yesterday_ncfile[variable][j]
                            found = True
                if not found and yesterday_exists:
                    for j, yt in enumerate(yesterday_ncfile['time'][:]):
                        if int(yt) == time:
                            data[i] = yesterday_ncfile[variable][j]
                            found = True
                if not found and today_exists:
                    for j, tt in enumerate(today_ncfile['time'][:]):
                        if int(tt) == time:
                            data[i] = today_ncfile[variable][j]

            pc = ax.pcolormesh(x,y,data.T)
            ax.xaxis.set_minor_locator(mdates.HourLocator(byhour=range(0,24,2)))
            ax.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
            ax.xaxis.set_major_locator(mdates.DayLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M\n%Y/%m/%d"))
            ax.set_ylabel('Altitude (m)', fontsize=17)
            ax.set_xlabel('Time (UTC)', fontsize=17)
            #ax.set_title('Last 24 hours', fontsize=19)
            ax.tick_params(axis='both', which='both', labelsize=14)
            ax.grid(axis='both', which='both')

            if n == 0:
                add_text(ax,plt,'NCAS Radar Wind Profiler 1\nCapel Dewi Atmospheric Observatory, Wales, UK')

            cbar = fig.colorbar(pc, ax = ax)
            cbar.ax.set_ylabel(f'{variable} ({ncfile[variable].units})', fontsize=17)
            cbar.ax.tick_params(axis='both', which='both', labelsize=12)
    else:
        # data for empty plot
        x_time = create_time_xaxis(15, days = 2)
        x_time = [dt.datetime.utcfromtimestamp(time) for time in x_time]
        y_altitude = np.linspace(0,8000,9)
        data = np.ma.ones((len(x_time),len(y_altitude))) * -99999
        data = np.ma.masked_where(data == -99999, data)
        x,y = np.meshgrid(x_time,y_altitude)
        no_plots = len(variables)
        fig = plt.figure(figsize=(20,8*no_plots))
        fig.set_facecolor('white')
        for n in range(no_plots):
            variable = variables[n]
            ax = fig.add_subplot(no_plots,1,n+1)
            pc = ax.pcolormesh(x,y,data.T)
            ax.xaxis.set_minor_locator(mdates.HourLocator(byhour=range(0,24,2)))
            ax.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
            ax.xaxis.set_major_locator(mdates.DayLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M\n%Y/%m/%d"))
            ax.set_ylabel('Altitude (m)', fontsize=17)
            ax.set_xlabel('Time (UTC)', fontsize=17)
            ax.tick_params(axis='both', which='both', labelsize=14)
            ax.grid(axis='both', which='both')
            if n == 0:
                add_text(ax,plt,'NCAS Radar Wind Profiler 1\nCapel Dewi Atmospheric Observatory, Wales, UK')

            cbar = fig.colorbar(pc, ax = ax)
            cbar.ax.set_ylabel(f'{variable}', fontsize=17)
            cbar.ax.tick_params(axis='both', which='both', labelsize=12)

    add_text(ax,plt,'NCAS Radar Wind Profiler 1\nCapel Dewi Atmospheric Observatory, Wales, UK')    

    plt.tight_layout()
    plt.savefig(f'{save_loc}/ncas-wind-profiler-1_{mode}-mode_multipanel_last-48-hours.png')
    plt.savefig(f'{save_loc}/ncas-wind-profiler-1_{mode}-mode_multipanel_last-48-hours.pdf')
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

    for var in ['upward_air_velocity']:   
        simple_2d_plot_last24(var, f'{nc_file_path}/{yesterday_file}', f'{nc_file_path}/{today_file}', plots_path, cmap='RdBu_r', zero_centre_cbar=True) 
        simple_2d_plot_last48(var, f'{nc_file_path}/{day_before_yesterday_file}', f'{nc_file_path}/{yesterday_file}', f'{nc_file_path}/{today_file}', plots_path, cmap='RdBu_r', zero_centre_cbar=True)

    for var in ['signal_to_noise_ratio_minimum', 'spectral_width_of_beam_3']:
        simple_2d_plot_last24(var, f'{nc_file_path}/{yesterday_file}', f'{nc_file_path}/{today_file}', plots_path)
        simple_2d_plot_last48(var, f'{nc_file_path}/{day_before_yesterday_file}', f'{nc_file_path}/{yesterday_file}', f'{nc_file_path}/{today_file}', plots_path)

    multi_plot_24hrs(['upward_air_velocity', 'signal_to_noise_ratio_minimum', 'spectral_width_of_beam_3'], f'{nc_file_path}/{yesterday_file}', f'{nc_file_path}/{today_file}', plots_path)
    multi_plot_48hrs(['upward_air_velocity', 'signal_to_noise_ratio_minimum', 'spectral_width_of_beam_3'], f'{nc_file_path}/{day_before_yesterday_file}', f'{nc_file_path}/{yesterday_file}', f'{nc_file_path}/{today_file}', plots_path)


if __name__ == "__main__":
    main(mode="low")
    main(mode="high")
