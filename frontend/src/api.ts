const base = import.meta.env.VITE_API_BASE ?? "";

export type Departure = {
  train_number: number;
  departure_station: string;
  arrival_station: string;
  departure_time: string;
  arrival_time: string;
};

export type SeatInfo = {
  ticket_number: string;
  full_name: string;
  train_number: number;
  seat_number: number;
  wagon_number?: number;
};

export async function fetchDepartures(): Promise<Departure[]> {
  const r = await fetch(`${base}/api/departures`);
  if (!r.ok) throw new Error("Не удалось загрузить расписание");
  return r.json();
}

export async function login(ticketNumber: string, passportSeries: string): Promise<string> {
  const r = await fetch(`${base}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      ticket_number: ticketNumber,
      passport_series: passportSeries,
    }),
  });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) {
    throw new Error((data as { detail?: string }).detail ?? "Ошибка входа");
  }
  return (data as { access_token: string }).access_token;
}

export async function fetchSeat(token: string): Promise<SeatInfo> {
  const r = await fetch(`${base}/api/me/seat`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) {
    throw new Error((data as { detail?: string }).detail ?? "Не удалось получить место");
  }
  return data as SeatInfo;
}
