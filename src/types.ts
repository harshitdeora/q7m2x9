export type Row = {startTime:string;hour:number;forecast:number|null;actual:number|null;error:number|null;publishTime:string|null;ageHours:number|null;actualHalfHours:number};
export type Metrics = {count:number;mae:number|null;rmse:number|null;bias:number|null;p90_absolute_error:number|null};
export type Decision = {decisionDate:string;cutoff:string;asOf:string;deliveryDate:string;rows:Row[];metrics:Metrics;coverage:number;expected:number;forecastEnergyMWh:number|null;meanForecastMW:number|null;latestPublication:string|null;oldestAgeHours:number|null;peak:Row|null;largestError:Row|null};
export type Accuracy = {metrics:Metrics;days:({decisionDate:string;deliveryDate:string;coverage:number}&Metrics)[];hourly:({hour:number}&Metrics)[];expected:number;forecastCoverage:number};
export type Provenance = {retrieved_at:string;sha256_uncompressed:string;records:Record<string,number>;sources:string[];decision_dates:string[];delivery_dates:string[]};
