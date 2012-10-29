using System;

namespace HRTBusAPI.API
{
    public class BusCheckinModel
    {
        public int id { get; set; }
        public int route { get; set; }
        public int stop { get; set; }
        public int direction { get; set; }
        public DateTime datetime { get; set; }
        public double lat { get; set; }
        public double lon { get; set; }
        public int adherence { get; set; }

        public BusCheckinModel(BusCheckin checkin)
        {
            id = checkin.BusId;
            route = checkin.Route;
            stop = checkin.StopId;
            direction = checkin.Direction;
            datetime = checkin.CheckinTime;
            lat = checkin.Lat;
            lon = checkin.Lon;
            adherence = checkin.Adherence;
        }
    }
}