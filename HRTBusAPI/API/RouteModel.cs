using System.Collections.Generic;

namespace HRTBusAPI.API
{
    public class RouteModel
    {
        public int route { get; set; }
        public List<BusCheckinModel> buses = new List<BusCheckinModel>();
    }
}