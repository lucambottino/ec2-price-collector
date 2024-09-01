export async function GET(req) {
  const { searchParams } = new URL(req.url);
  const exchange = searchParams.get("exchange");

  try {
    const response = await fetch(
      `http://nestjs:3000/latest-coin-data/exchange?exchange=${exchange}`
    );
    if (!response.ok) {
      throw new Error("Failed to fetch data from NestJS");
    }
    const data = await response.json();
    return new Response(JSON.stringify(data), { status: 200 });
  } catch (error) {
    console.error("Error fetching data:", error);
    return new Response(JSON.stringify({ error: "Failed to fetch data" }), {
      status: 500,
    });
  }
}
