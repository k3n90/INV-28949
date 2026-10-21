type Good = {
  id: string;
  name: string;
  imageUrl: string;
  created: string;
};

async function loadGoods(): Promise<Good[]> {
  const base = process.env.API_URL ?? "http://api:8000";
  const response = await fetch(`${base}/api/products`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`catalog responded ${response.status}`);
  }
  return response.json();
}

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const items = await loadGoods();

  return (
    <main>
      <h2>Каталог</h2>
      {items.length === 0 ? (
        <p>Пока пусто</p>
      ) : (
        <div className="goods">
          {items.map((item) => (
            <div className="good" key={item.id}>
              <img src={item.imageUrl} alt={item.name} />
              <p>{item.name}</p>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}
