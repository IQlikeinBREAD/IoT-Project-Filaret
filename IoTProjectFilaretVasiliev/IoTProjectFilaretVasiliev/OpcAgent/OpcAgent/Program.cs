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

    var readNodes = new OpcReadNode[deviceCount];
    int index = 0;
    foreach (var endpoint in endpoints)
    {
        if (endpoint.NamespaceUri == "ns=2" && endpoint.BrowsePath.Contains("/Device"))
        {
            var deviceId = endpoint.BrowsePath.Substring(5);

            readNodes[index] = new OpcReadNode("ns=2;s={0}/ProductionStatus", deviceId);

            readNodes[++index] = new OpcReadNode("ns=2;s={0}/ProductionRate", deviceId);

            readNodes[++index] = new OpcReadNode("ns=2;s={0}/WorkorderId", deviceId);

            readNodes[++index] = new OpcReadNode("ns=2;s={0}/Temperature", deviceId);

            readNodes[++index] = new OpcReadNode("ns=2;s={0}/GoodCount", deviceId);

            readNodes[++index] = new OpcReadNode("ns=2;s={0}/BadCount", deviceId);

            readNodes[++index] = new OpcReadNode("ns=2;s={0}/DeviceError", deviceId);
        }
    }

    var job = client.ReadNodes(readNodes);

    foreach (var item in job)
    {
        Console.WriteLine($"Device: {item.NodeId}, Value: {item.Value}");
    }
}
