import { useCallback, useEffect, useState } from "react";
import type { Departure, SeatInfo } from "./api";
import { fetchDepartures, fetchSeat, login } from "./api";

export default function App() {
  const [departures, setDepartures] = useState<Departure[]>([]);
  const [depErr, setDepErr] = useState<string | null>(null);
  const [ticket, setTicket] = useState("");
  const [series, setSeries] = useState("");
  const [authErr, setAuthErr] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(() => sessionStorage.getItem("rail_token"));
  const [seat, setSeat] = useState<SeatInfo | null>(null);
  const [loadingDeps, setLoadingDeps] = useState(true);
  const [loadingAuth, setLoadingAuth] = useState(false);

  useEffect(() => {
    fetchDepartures()
      .then(setDepartures)
      .catch((e: Error) => setDepErr(e.message))
      .finally(() => setLoadingDeps(false));
  }, []);

  const loadSeat = useCallback(async (t: string) => {
    const s = await fetchSeat(t);
    setSeat(s);
  }, []);

  useEffect(() => {
    if (token) {
      loadSeat(token).catch((e: Error) => {
        setAuthErr(e.message);
        setToken(null);
        sessionStorage.removeItem("rail_token");
      });
    } else {
      setSeat(null);
    }
  }, [token, loadSeat]);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setAuthErr(null);
    setLoadingAuth(true);
    try {
      const t = await login(ticket.trim(), series.trim());
      sessionStorage.setItem("rail_token", t);
      setToken(t);
    } catch (err) {
      setAuthErr(err instanceof Error ? err.message : "Ошибка");
    } finally {
      setLoadingAuth(false);
    }
  }

  function logout() {
    sessionStorage.removeItem("rail_token");
    setToken(null);
    setSeat(null);
    setAuthErr(null);
  }

  return (
    <>
      <header>
        <h1>Расписание отправлений</h1>
        <p className="subtitle">
          Экзаменационный билет №7 · Железнодорожная компания · <strong>RomanovSV</strong>
        </p>
      </header>

      <section className="panel">
        <h2>Отправления поездов</h2>
        {depErr && <p className="error">{depErr}</p>}
        {loadingDeps ? (
          <p className="subtitle">Загрузка…</p>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table>
              <thead>
                <tr>
                  <th>№ поезда</th>
                  <th>Отправление</th>
                  <th>Прибытие</th>
                  <th>Отпр.</th>
                  <th>Приб.</th>
                </tr>
              </thead>
              <tbody>
                {departures.map((d) => (
                  <tr key={d.train_number}>
                    <td>{d.train_number}</td>
                    <td>{d.departure_station}</td>
                    <td>{d.arrival_station}</td>
                    <td>{d.departure_time}</td>
                    <td>{d.arrival_time}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="panel">
        <h2>
          Моё место в поезде
          {token && <span className="badge">в системе</span>}
        </h2>
        {!token ? (
          <form onSubmit={onSubmit}>
            <div className="form-row">
              <label>
                Номер билета
                <input
                  value={ticket}
                  onChange={(e) => setTicket(e.target.value)}
                  autoComplete="off"
                  required
                />
              </label>
              <label>
                Серия паспорта
                <input
                  value={series}
                  onChange={(e) => setSeries(e.target.value)}
                  autoComplete="off"
                  required
                />
              </label>
            </div>
            {authErr && <p className="error">{authErr}</p>}
            <button type="submit" disabled={loadingAuth}>
              {loadingAuth ? "Проверка…" : "Войти"}
            </button>
          </form>
        ) : (
          <>
            {authErr && <p className="error">{authErr}</p>}
            {seat && (
              <div className="seat-card">
                <dl>
                  <dt>Пассажир</dt>
                  <dd>{seat.full_name}</dd>
                  <dt>Билет</dt>
                  <dd>№ {seat.ticket_number}</dd>
                  <dt>Поезд</dt>
                  <dd>{seat.train_number}</dd>
                  <dt>Место</dt>
                  <dd>{seat.seat_number}</dd>
                  {seat.wagon_number != null && (
                    <>
                      <dt>Вагон</dt>
                      <dd>{seat.wagon_number}</dd>
                    </>
                  )}
                </dl>
                <button type="button" className="secondary" onClick={logout}>
                  Выйти
                </button>
              </div>
            )}
          </>
        )}
      </section>

      <p className="footer-note">
        Аутентификация: сверка номера билета и серии паспорта с данными в БД.
      </p>
    </>
  );
}
