# install siphon: https://anaconda.org/conda-forge/siphon
import pandas as pd
import pvlib
import matplotlib.pyplot as plt

import datetime

# import pvlib forecast models
from pvlib.forecast import GFS, NAM, NDFD, HRRR, RAP

# specify location (Tucson, AZ)
latitude, longitude, tz = 32.2, -110.9, 'US/Arizona'

# specify time range.
start = pd.Timestamp(datetime.date.today(), tz=tz)

end = start + pd.Timedelta(days=7)

irrad_vars = ['ghi', 'dni', 'dhi']


# GFS model, defaults to 0.5 degree resolution
# 0.25 deg available
model = GFS()

# retrieve data. returns pandas.DataFrame object
raw_data = model.get_data(latitude, longitude, start, end)

print(raw_data.head())


data = raw_data

# rename the columns according the key/value pairs in model.variables.
data = model.rename(data)

# convert temperature
data['temp_air'] = model.kelvin_to_celsius(data['temp_air'])

# convert wind components to wind speed
data['wind_speed'] = model.uv_to_speed(data)

# calculate irradiance estimates from cloud cover.
# uses a cloud_cover to ghi to dni model or a
# uses a cloud cover to transmittance to irradiance model.
# this step is discussed in more detail in the next section
irrad_data = model.cloud_cover_to_irradiance(data['total_clouds'])

data = data.join(irrad_data, how='outer')

# keep only the final data
data = data[model.output_variables]

print(data.head())


data = model.process_data(raw_data)

print(data.head())


data = model.get_processed_data(latitude, longitude, start, end)

print(data.head())


# plot cloud cover percentages
cloud_vars = ['total_clouds', 'low_clouds','mid_clouds', 'high_clouds']

data[cloud_vars].plot();

plt.ylabel('Cloud cover %');

plt.xlabel('Forecast Time ({})'.format(tz));

plt.title('GFS 0.5 deg forecast for lat={}, lon={}'.format(latitude, longitude));


plt.legend();


# plot irradiance data
data = model.rename(raw_data)

irrads = model.cloud_cover_to_irradiance(data['total_clouds'], how='clearsky_scaling')

irrads.plot();

plt.ylabel('Irradiance ($W/m^2$)');

plt.xlabel('Forecast Time ({})'.format(tz));

plt.title('GFS 0.5 deg forecast for lat={}, lon={} using "clearsky_scaling"'
           .format(latitude, longitude));


plt.legend();


# plot irradiance data
irrads = model.cloud_cover_to_irradiance(data['total_clouds'], how='liujordan')

irrads.plot();

plt.ylabel('Irradiance ($W/m^2$)');

plt.xlabel('Forecast Time ({})'.format(tz));

plt.title('GFS 0.5 deg forecast for lat={}, lon={} using "liujordan"'
           .format(latitude, longitude));


plt.legend();


resampled_data = data.resample('5min').interpolate()

resampled_irrads = model.cloud_cover_to_irradiance(resampled_data['total_clouds'], how='clearsky_scaling')

resampled_irrads.plot();

plt.ylabel('Irradiance ($W/m^2$)');

plt.xlabel('Forecast Time ({})'.format(tz));

plt.title('GFS 0.5 deg forecast for lat={}, lon={} resampled'
           .format(latitude, longitude));
 

plt.legend();


model = HRRR()

data = model.get_processed_data(latitude, longitude, start, end)

data[irrad_vars].plot();

plt.ylabel('Irradiance ($W/m^2$)');

plt.xlabel('Forecast Time ({})'.format(tz));

plt.title('HRRR 3 km forecast for lat={}, lon={}'
           .format(latitude, longitude));
 

plt.legend();


model = RAP()

data = model.get_processed_data(latitude, longitude, start, end)

data[irrad_vars].plot();

plt.ylabel('Irradiance ($W/m^2$)');

plt.xlabel('Forecast Time ({})'.format(tz));

plt.title('RAP 13 km forecast for lat={}, lon={}'
           .format(latitude, longitude));
 

plt.legend();


model = NAM()

data = model.get_processed_data(latitude, longitude, start, end)

data[irrad_vars].plot();

plt.ylabel('Irradiance ($W/m^2$)');

plt.xlabel('Forecast Time ({})'.format(tz));

plt.title('NAM 20 km forecast for lat={}, lon={}'
           .format(latitude, longitude));
 

plt.legend();


model = NDFD()

data = model.get_processed_data(latitude, longitude, start, end)

data[irrad_vars].plot();

plt.ylabel('Irradiance ($W/m^2$)');

plt.xlabel('Forecast Time ({})'.format(tz));

plt.title('NDFD forecast for lat={}, lon={}'
            .format(latitude, longitude));
plt.legend();
#plt.close();


from pvlib.pvsystem import PVSystem, retrieve_sam

from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS

from pvlib.tracking import SingleAxisTracker

from pvlib.modelchain import ModelChain

sandia_modules = retrieve_sam('sandiamod')

cec_inverters = retrieve_sam('cecinverter')

module = sandia_modules['Canadian_Solar_CS5P_220M___2009_']

inverter = cec_inverters['SMA_America__SC630CP_US__with_ABB_EcoDry_Ultra_transformer_']

temperature_model_parameters = TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']

# model a big tracker for more fun
system = SingleAxisTracker(module_parameters=module, inverter_parameters=inverter, temperature_model_parameters=temperature_model_parameters, modules_per_string=15, strings_per_inverter=300)

# fx is a common abbreviation for forecast
fx_model = GFS()

fx_data = fx_model.get_processed_data(latitude, longitude, start, end)

# use a ModelChain object to calculate modeling intermediates
mc = ModelChain(system, fx_model.location)

# extract relevant data for model chain
mc.run_model(fx_data);


mc.total_irrad.plot();

plt.ylabel('Plane of array irradiance ($W/m^2$)');

plt.legend(loc='best');


mc.cell_temperature.plot();

plt.ylabel('Cell Temperature (C)');


#…and finally AC power…
mc.ac.fillna(0).plot();

plt.ylim(0, None);

plt.ylabel('AC Power (W)');
