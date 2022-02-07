pub use std::{
    fs::{create_dir_all, read_dir, File},
    io::{BufRead, BufReader, Error, Write},
    time::{Duration, Instant},
};

use nmea_parser::ais::{VesselDynamicData, VesselStaticData};

use crate::db::{
    get_db_conn, sqlite_createtable_dynamicreport, sqlite_createtable_staticreport,
    sqlite_insert_dynamic, sqlite_insert_static,
};
use crate::decode::VesselData;

// TODO: write new epoch_2_dt for exactearth timestamp
//use crate::util::epoch_2_dt;

pub fn decodemsgs_ee_csv(filename: &str) -> (Vec<VesselData>, Vec<VesselData>) {
    assert_eq!(&filename[&filename.len() - 4..], ".csv");

    let mut reader = csv::Reader::from_reader(
        File::open(filename).expect(format!("cannot open file {}", filename).as_str()),
    );
    let mut stat_msgs = <Vec<VesselData>>::new();
    let mut positions = <Vec<VesselData>>::new();

    for row in reader.records() {
        println!("{:?}", row.unwrap());
    }

    (stat_msgs, positions)
}

#[cfg(test)]
pub mod tests {

    use crate::decodemsgs_ee_csv;
    use crate::Error;
    use std::fs::File;
    use std::io::Write;
    pub use std::{
        fs::{create_dir_all, read_dir},
        io::{BufRead, BufReader},
        time::{Duration, Instant},
    };

    pub fn testingdata() -> Result<(), &'static str> {
        let c = r#"
MMSI,Message_ID,Repeat_indicator,Time,Millisecond,Region,Country,Base_station,Online_data,Group_code,Sequence_ID,Channel,Data_length,Vessel_Name,Call_sign,IMO,Ship_Type,Dimension_to_Bow,Dimension_to_stern,Dimension_to_port,Dimension_to_starboard,Draught,Destination,AIS_version,Navigational_status,ROT,SOG,Accuracy,Longitude,Latitude,COG,Heading,Regional,Maneuver,RAIM_flag,Communication_flag,Communication_state,UTC_year,UTC_month,UTC_day,UTC_hour,UTC_minute,UTC_second,Fixing_device,Transmission_control,ETA_month,ETA_day,ETA_hour,ETA_minute,Sequence,Destination_ID,Retransmit_flag,Country_code,Functional_ID,Data,Destination_ID_1,Sequence_1,Destination_ID_2,Sequence_2,Destination_ID_3,Sequence_3,Destination_ID_4,Sequence_4,Altitude,Altitude_sensor,Data_terminal,Mode,Safety_text,Non-standard_bits,Name_extension,Name_extension_padding,Message_ID_1_1,Offset_1_1,Message_ID_1_2,Offset_1_2,Message_ID_2_1,Offset_2_1,Destination_ID_A,Offset_A,Increment_A,Destination_ID_B,offsetB,incrementB,data_msg_type,station_ID,Z_count,num_data_words,health,unit_flag,display,DSC,band,msg22,offset1,num_slots1,timeout1,Increment_1,Offset_2,Number_slots_2,Timeout_2,Increment_2,Offset_3,Number_slots_3,Timeout_3,Increment_3,Offset_4,Number_slots_4,Timeout_4,Increment_4,ATON_type,ATON_name,off_position,ATON_status,Virtual_ATON,Channel_A,Channel_B,Tx_Rx_mode,Power,Message_indicator,Channel_A_bandwidth,Channel_B_bandwidth,Transzone_size,Longitude_1,Latitude_1,Longitude_2,Latitude_2,Station_Type,Report_Interval,Quiet_Time,Part_Number,Vendor_ID,Mother_ship_MMSI,Destination_indicator,Binary_flag,GNSS_status,spare,spare2,spare3,spare4
"432448000","1","0","20211201_220415","80","66","","","","None","","","[28]","","","","","","","","","","","","7","0.0","3.5","0","-34.0796816667","14.69666","78.9","86.0","","0","0","","33286","","","","","","12","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","","",""
"210335000","3","0","20211201_220450","450","66","","","","None","","","[28]","","","","","","","","","","","","0","0.0","13.9","0","152.655881667","-13.4423183333","164.2","164.0","","0","0","","11473","","","","","","47","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","","",""
"374651000","1","0","20211201_220809","620","66","","","","None","","","[28]","","","","","","","","","","","","0","1.11600720834","13.3","0","-53.2738666667","8.10760166667","118.2","120.0","","0","0","","27680","","","","","","4","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","","",""
"338789000","27","3","20211201_220853","630","66","","","","None","","","[16]","","","","","","","","","","","","0","","22.0","0","-77.68","27.9216666667","309.0","","","","0","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","0","","",""
"367404840","18","0","20211201_220919","460","66","","","","None","","","[28]","","","","","","","","","","","","","","1.7","0","170.216968333","17.7062233333","164.2","None","0","","0","1","393222","","","","","","14","","","","","","","","","","","","","","","","","","","","","","","","0","","","","","","","","","","","","","","","","","","","","","","1","0","1","1","1","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","","",""
"993116106","21","0","20211201_220554","440","66","","","","None","","","[46]","","","","","0","0","0","0","","","","","","","0","-54.9975633333","8.97102","","","","","1","","","","","","","","60","1","","","","","","","","","","","","","","","","","","","","","","","0","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","1","R TETHYS CABLE","0","0","1","","","","","","","","","","","","","","","","","","","","","","0","","",""
"211188900","27","3","20211201_221929","30","66","","","","None","","","[16]","","","","","","","","","","","","1","","0.0","1","10.4816666667","53.2416666667","None","","","","1","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","0","","",""
"538007477","1","0","20211201_221951","530","66","","","","None","","","[28]","","","","","","","","","","","","8","0.0","1.9","1","-132.0437","54.24265","98.0","182.0","","0","0","","49155","","","","","","49","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","","",""
"212352000","1","0","20211201_222012","680","66","","","","None","","","[28]","","","","","","","","","","","","0","-0.401762595001","17.4","0","-1.56493","-25.4976883333","124.4","125.0","","0","0","","49152","","","","","","6","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","","",""
"205532090","27","3","20211201_224933","620","66","","","","None","","","[16]","","","","","","","","","","","","0","","0.0","1","0.321666666667","49.48","None","","","","1","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","0","","",""
"355658000","1","0","20211201_225006","380","66","","","","None","","","[28]","","","","","","","","","","","","0","2.18737412834","18.2","0","166.964766667","37.01234","65.4","68.0","","0","0","","49153","","","","","","2","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","","",""
"257302140","27","3","20211201_225835","510","66","","","","None","","","[16]","","","","","","","","","","","","0","","9.0","0","5.10833333333","62.0783333333","166.0","","","","0","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","0","","",""
"371785000","3","0","20211201_225858","100","66","","","","None","","","[28]","","","","","","","","","","","","2","None","0.5","0","179.640936667","-8.92283833333","241.2","226.0","","0","0","","0","","","","","","52","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","","",""
"538009104","27","3","20211201_224522","880","66","","","","None","","","[16]","","","","","","","","","","","","0","","10.0","0","104.365","1.31666666667","47.0","","","","0","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","0","","",""
"354850000","1","0","20211201_224601","310","66","","","","None","","","[28]","","","","","","","","","","","","0","7.54420872835","15.6","1","154.368973333","28.7149916667","301.5","300.0","","0","0","","81923","","","","","","26","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","","",""
"244750503","27","3","20211201_220230","770","66","","","","None","","","[16]","","","","","","","","","","","","15","","0.0","0","4.99666666667","51.87","None","","","","0","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","0","","",""
"503066000","27","3","20211201_220254","170","66","","","","None","","","[16]","","","","","","","","","","","","5","","0.0","0","115.008333333","-21.68","96.0","","","","1","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","0","","",""
"601005500","1","0","20211201_222723","420","66","","","","None","","","[28]","","","","","","","","","","","","7","None","4.8","1","26.0865566667","-34.2307733333","39.8","None","","0","1","","33600","","","","","","22","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","","",""
"244061000","27","3","20211201_222801","580","66","","","","None","","","[16]","","","","","","","","","","","","0","","12.0","1","9.89666666667","53.54","83.0","","","","0","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","0","","",""
"209213000","27","3","20211201_222817","600","66","","","","None","","","[16]","","","","","","","","","","","","1","","0.0","1","3.62166666667","51.415","152.0","","","","0","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","0","","",""
"372932000","27","3","20211201_222438","540","66","","","","None","","","[16]","","","","","","","","","","","","0","","19.0","0","103.06","1.45833333333","119.0","","","","0","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","0","","",""
"636019497","1","0","20211201_222511","570","66","","","","None","","","[28]","","","","","","","","","","","","0","0.0","14.1","1","-81.611365","18.193895","132.4","131.0","","0","0","","33084","","","","","","4","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","","",""
"548335100","25","0","20211201_222935","810","66","","","","None","","","[28]","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","187496a8ab3d67cdf4b9c39642de4b2c","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","0","","","","",""
"311000206","3","0","20211201_222953","630","66","","","","None","","","[28]","","","","","","","","","","","","1","0.0","0.1","0","32.0766816667","-28.895985","80.4","47.0","","0","0","","84938","","","","","","53","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","","",""
"431602337","27","3","20211201_221229","630","66","","","","None","","","[16]","","","","","","","","","","","","1","","0.0","0","133.568333333","33.5116666667","164.0","","","","0","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","0","","",""
"538090451","1","0","20211201_221251","500","66","","","","None","","","[28]","","","","","","","","","","","","0","-6.42820152001","15.7","0","4.88901","-13.3330366667","315.1","315.0","","0","0","","2249","","","","","","46","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","","",""
"477723200","1","0","20211201_221318","410","66","","","","None","","","[28]","","","","","","","","","","","","0","3.61586335501","17.5","0","153.144901667","-31.9049866667","7.9","8.0","","0","0","","27700","","","","","","11","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","","",""
"232015624","27","3","20211201_220742","530","66","","","","None","","","[16]","","","","","","","","","","","","5","","0.0","1","-157.951666667","21.3533333333","187.0","","","","0","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","0","","",""
"413510730","27","3","20211201_220816","100","66","","","","None","","","[16]","","","","","","","","","","","","0","","12.0","0","113.601666667","22.0516666667","215.0","","","","0","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","0","","",""
"226105000","27","3","20211201_223743","610","66","","","","None","","","[16]","","","","","","","","","","","","0","","3.0","0","-9.64166666667","57.5583333333","181.0","","","","0","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","0","","",""
"255806512","1","0","20211201_223805","390","66","","","","None","","","[28]","","","","","","","","","","","","0","0.0","13.2","0","-113.7041","22.4757","119.0","120.0","","0","0","","27796","","","","","","55","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","","",""
"373076000","3","0","20211201_223233","740","66","","","","None","","","[28]","","","","","","","","","","","","0","0.0","10.9","1","-169.435366667","51.4281866667","79.6","65.0","","0","0","","73677","","","","","","23","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","","",""
"414278590","27","3","20211201_223253","990","66","","","","None","","","[16]","","","","","","","","","","","","15","","0.0","1","121.085","33.2966666667","None","","","","1","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","0","","",""
"566983000","27","3","20211201_224423","660","66","","","","None","","","[16]","","","","","","","","","","","","3","","0.0","0","-2.93666666667","4.53833333333","4.0","","","","0","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","0","","",""
"339202000","27","3","20211201_224500","920","66","","","","None","","","[16]","","","","","","","","","","","","5","","0.0","0","-80.0483333333","26.7133333333","130.0","","","","0","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","0","","",""
"367657270","27","3","20211201_225922","130","66","","","","None","","","[16]","","","","","","","","","","","","0","","10.0","0","168.18","31.7133333333","270.0","","","","0","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","0","","",""
"311000387","1","0","20211201_225958","850","66","","","","None","","","[28]","","","","","","","","","","","","0","-1.60705038","14.3","0","159.615465","34.2145016667","73.5","81.0","","0","0","","114691","","","","","","58","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","","",""
"477045500","1","0","20211201_223931","847","66","","","","None","","","[28]","","","","","","","","","","","","0","-1.11600720834","0.6","0","151.945833333","-33.156165","243.2","208.0","","0","0","","114738","","","","","","19","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","","",""
"503774000","1","0","20211201_224258","539","66","","","","None","","","[28]","","","","","","","","","","","","0","None","9.0","0","153.270383333","-27.2147183333","34.3","None","","0","0","","81937","","","","","","2","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","","",""
"354227000","1","0","20211201_222117","480","66","","","","None","","","[28]","","","","","","","","","","","","0","0.0","11.4","0","-19.3662866667","19.727565","24.2","26.0","","0","0","","27732","","","","","","12","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","","",""
"735058312","18","3","20211201_222142","950","66","","","","None","","","[28]","","","","","","","","","","","","","","9.4","1","-90.3051516667","-0.487873333333","109.2","None","0","","1","1","0","","","","","","40","","","","","","","","","","","","","","","","","","","","","","","","0","","","","","","","","","","","","","","","","","","","","","","1","0","1","1","1","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","","",""
"412421067","24","0","20211201_221838","450","66","","","","None","","","[28]","","BZW5J","","30","35","25","5","4","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","1","U/=2A'I","","","","","38","","",""
"269057587","27","3","20211201_221907","340","66","","","","None","","","[16]","","","","","","","","","","","","0","","7.0","1","5.41333333333","51.93","308.0","","","","1","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","0","","",""
"538007971","3","0","20211201_222930","231","66","","","","None","","","[28]","","","","","","","","","","","","1","0.0","0.1","0","-15.4054216667","28.10836","330.1","39.0","","0","0","","86778","","","","","","31","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","","",""
"81562826","24","0","20211201_190606","410","66","","","","None","","","[27]","CI012-16","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","0","","","","","","","","",""
"#;

        if create_dir_all("testdata/").is_ok() {
            let mut output = File::create("testdata/testingdata.csv").unwrap();
            let _ = write!(output, "{}", c);
            Ok(())
        } else {
            Err("cant create testing data dir!")
        }
    }

    #[test]
    pub fn test_csv() -> Result<(), Error> {
        let _ = testingdata();

        let fpath = std::path::PathBuf::from("testdata/testingdata.csv");

        let (positions, stat_msgs) = decodemsgs_ee_csv(&fpath.to_str().unwrap());

        Ok(())
    }
}
