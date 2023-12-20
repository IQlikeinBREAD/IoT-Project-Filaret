using Opc.UaFx;
using Opc.UaFx.Client;

using (var client = new OpcClient("opc.tcp://localhost:4840/"))
{
    client.Connect();

    var endpoints = client.EnumerateEndpoints();

    int deviceCount = 0;
    foreach (var endpoint in endpoints)
    {
        if (endpoint.NamespaceUri == "ns=2" && endpoint.BrowsePath.Contains("/Device"))
        {
            deviceCount++;
        }
    }

    Console.WriteLine("Number of devices: {0}", deviceCount);

    // Prepare read nodes for all devices
    var readNodes = new OpcReadNode[deviceCount];
    int index = 0;
    foreach (var endpoint in endpoints)
    {
        if (endpoint.NamespaceUri == "ns=2" && endpoint.BrowsePath.Contains("/Device"))
        {
            var deviceId = endpoint.BrowsePath.Substring(5);

            // Read node for "ProductionStatus"
            readNodes[index] = new OpcReadNode("ns=2;s={0}/ProductionStatus", deviceId);

            // Read node for "ProductionRate"
            readNodes[++index] = new OpcReadNode("ns=2;s={0}/ProductionRate", deviceId);

            // Read node for "WorkorderId"
            readNodes[++index] = new OpcReadNode("ns=2;s={0}/WorkorderId", deviceId);

            // Read node for "Temperature"
            readNodes[++index] = new OpcReadNode("ns=2;s={0}/Temperature", deviceId);

            // Read node for "GoodCount"
            readNodes[++index] = new OpcReadNode("ns=2;s={0}/GoodCount", deviceId);

            // Read node for "BadCount"
            readNodes[++index] = new OpcReadNode("ns=2;s={0}/BadCount", deviceId);

            // Read node for "DeviceError"
            readNodes[++index] = new OpcReadNode("ns=2;s={0}/DeviceError", deviceId);
        }
    }

    // Perform read operation for all devices
    var job = client.ReadNodes(readNodes);

    // Iterate through the result and print the values
    foreach (var item in job)
    {
        Console.WriteLine($"Device: {item.NodeId}, Value: {item.Value}");
    }
}
