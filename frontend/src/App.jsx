import { useEffect, useMemo, useState } from 'react'
import { MapContainer, TileLayer, CircleMarker, Circle, Popup, useMap } from 'react-leaflet'
import {
  LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts'
import 'leaflet/dist/leaflet.css'
import './App.css'
import { useGeoLog, toMs } from './hooks/useGeoLog'

// Pontos de referência para a busca por raio (o usuário escolhe um deles).
const PONTOS_REFERENCIA = [
  { nome: 'Centro (João Pessoa)', lat: -7.115, lng: -34.873 },
  { nome: 'Cabo Branco', lat: -7.121, lng: -34.832 },
  { nome: 'Tibiri / BR-230', lat: -7.15, lng: -34.95 },
]

const LIMITE_VELOCIDADE = 80
const CORES_STATUS = { Ativo: '#16a34a', 'Em Descanso': '#f59e0b' }
const CORES_LINHAS = ['#2563eb', '#dc2626', '#16a34a', '#f59e0b', '#7c3aed', '#0891b2']

/* Distância em km (Haversine). Usada SÓ para mostrar "a X km" no popup.
   Quem decide quais veículos estão dentro do raio é o MongoDB ($geoNear). */
function distanciaKm(lat1, lng1, lat2, lng2) {
  const R = 6371
  const rad = (g) => (g * Math.PI) / 180
  const dLat = rad(lat2 - lat1)
  const dLng = rad(lng2 - lng1)
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(rad(lat1)) * Math.cos(rad(lat2)) * Math.sin(dLng / 2) ** 2
  return 2 * R * Math.asin(Math.sqrt(a))
}

const formatarHora = (ts) =>
  new Date(toMs(ts)).toLocaleString('pt-BR', {
    day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit',
  })

// Recentraliza o mapa quando o usuário troca a referência.
// (Recebe lat/lng separados: um array novo a cada render faria o mapa "pular" sozinho.)
function Recentralizar({ lat, lng }) {
  const map = useMap()
  useEffect(() => {
    map.setView([lat, lng])
  }, [lat, lng, map])
  return null
}

export default function App() {
  const [refIndex, setRefIndex] = useState(0)
  const [raioKm, setRaioKm] = useState(10)
  const [auto, setAuto] = useState(false)

  const referencia = PONTOS_REFERENCIA[refIndex]
  const centro = [referencia.lat, referencia.lng]

  const {
    motoristas, telemetrias, frota, idsNoRaio,
    aoVivo, carregando, erro, simularMovimentacao,
  } = useGeoLog(referencia, raioKm)

  // Simulação automática (a cada 3 s) enquanto o checkbox estiver marcado.
  useEffect(() => {
    if (!auto) return
    const id = setInterval(simularMovimentacao, 3000)
    return () => clearInterval(id)
  }, [auto, simularMovimentacao])

  const dentroDoRaio = frota.filter((v) => idsNoRaio.has(v.veiculo_id))

  // KPIs
  const frotasAtivas = frota.filter((v) => v.status === 'Ativo').length
  const mediaTemp = frota.length
    ? frota.reduce((soma, v) => soma + v.temperatura, 0) / frota.length
    : 0
  const alertas = frota.filter((v) => v.velocidade > LIMITE_VELOCIDADE).length

  // Pizza: distribuição do status dos motoristas
  const dadosStatus = Object.entries(
    motoristas.reduce((acc, m) => ({ ...acc, [m.status]: (acc[m.status] ?? 0) + 1 }), {}),
  ).map(([name, value]) => ({ name, value }))

  // Linhas: histórico de temperatura por veículo (uma linha por placa, em ordem de tempo)
  const placas = useMemo(() => [...new Set(frota.map((v) => v.placa))], [frota])
  const historicoTemp = useMemo(
    () =>
      telemetrias
        .filter((t) => t.timestamp)
        .sort((a, b) => toMs(a.timestamp) - toMs(b.timestamp))
        .map((t) => ({ hora: formatarHora(t.timestamp), [t.veiculo.placa]: t.temperatura })),
    [telemetrias],
  )

  if (carregando) return <div className="app"><p>Carregando dados da frota…</p></div>

  return (
    <div className="app">
      <header>
        <h1>GeoLog · LogiTech Express</h1>
        <p>
          Monitoramento de frota em tempo real{' '}
          <span className={`badge ${aoVivo ? 'on' : 'off'}`}>
            {aoVivo ? '● ao vivo' : '○ desconectado'}
          </span>
        </p>
      </header>

      {erro && <div className="erro">{erro}</div>}

      {/* KPIs */}
      <section className="kpis">
        <div className="card">
          <span>Frotas ativas</span>
          <strong>{frotasAtivas}</strong>
        </div>
        <div className="card">
          <span>Temperatura média da carga</span>
          <strong>{mediaTemp.toFixed(1)} °C</strong>
        </div>
        <div className={`card ${alertas > 0 ? 'alerta' : ''}`}>
          <span>Alertas de velocidade (&gt; {LIMITE_VELOCIDADE} km/h)</span>
          <strong>{alertas}</strong>
        </div>
      </section>

      {/* Simulador (bônus) */}
      <section className="card simulador">
        <button onClick={simularMovimentacao}>Simular Movimentação</button>
        <label>
          <input type="checkbox" checked={auto} onChange={(e) => setAuto(e.target.checked)} />
          Automático (a cada 3 s)
        </label>
      </section>

      {/* Busca por raio + mapa */}
      <section className="card">
        <h2>Busca por raio</h2>
        <div className="filtros">
          <label>
            Ponto de referência
            <select value={refIndex} onChange={(e) => setRefIndex(Number(e.target.value))}>
              {PONTOS_REFERENCIA.map((p, i) => (
                <option key={p.nome} value={i}>{p.nome}</option>
              ))}
            </select>
          </label>
          <label>
            Raio: <b>{raioKm} km</b>
            <input
              type="range" min="1" max="30" value={raioKm}
              onChange={(e) => setRaioKm(Number(e.target.value))}
            />
          </label>
        </div>
        <p className="resumo">
          {dentroDoRaio.length} de {frota.length} veículos dentro do raio.
        </p>

        <MapContainer center={centro} zoom={11} className="mapa">
          <Recentralizar lat={referencia.lat} lng={referencia.lng} />
          <TileLayer
            attribution="&copy; OpenStreetMap"
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <Circle center={centro} radius={raioKm * 1000} pathOptions={{ color: '#2563eb', fillOpacity: 0.08 }} />
          <CircleMarker center={centro} radius={6} pathOptions={{ color: '#111', fillColor: '#111', fillOpacity: 1 }}>
            <Popup>Referência: {referencia.nome}</Popup>
          </CircleMarker>
          {frota.map((v) => {
            const dentro = idsNoRaio.has(v.veiculo_id)
            return (
              <CircleMarker
                key={v.veiculo_id}
                center={[v.lat, v.lng]}
                radius={10}
                pathOptions={{
                  color: dentro ? '#16a34a' : '#9ca3af',
                  fillColor: dentro ? '#16a34a' : '#9ca3af',
                  fillOpacity: 0.8,
                }}
              >
                <Popup>
                  <b>{v.placa}</b> · {v.modelo}<br />
                  Motorista: {v.motorista}<br />
                  Temp: {v.temperatura} °C · {v.velocidade} km/h<br />
                  A {distanciaKm(referencia.lat, referencia.lng, v.lat, v.lng).toFixed(1)} km da referência
                </Popup>
              </CircleMarker>
            )
          })}
        </MapContainer>
      </section>

      {/* Tabela unificada */}
      <section className="card">
        <h2>Visão unificada</h2>
        <div className="tabela-wrap">
          <table>
            <thead>
              <tr>
                <th>Motorista</th><th>Placa</th><th>Última temperatura</th>
                <th>Velocidade</th><th>Coordenadas</th>
              </tr>
            </thead>
            <tbody>
              {frota.map((v) => (
                <tr key={v.veiculo_id}>
                  <td>{v.motorista}</td>
                  <td>{v.placa}</td>
                  <td>{v.temperatura} °C</td>
                  <td className={v.velocidade > LIMITE_VELOCIDADE ? 'excesso' : ''}>
                    {v.velocidade} km/h {v.velocidade > LIMITE_VELOCIDADE && '⚠'}
                  </td>
                  <td>{v.lat.toFixed(3)}, {v.lng.toFixed(3)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Gráficos */}
      <section className="graficos">
        <div className="card">
          <h2>Histórico de temperatura por veículo</h2>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={historicoTemp}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hora" tick={{ fontSize: 11 }} />
              <YAxis unit="°C" />
              <Tooltip />
              <Legend />
              {placas.map((placa, i) => (
                <Line
                  key={placa} type="monotone" dataKey={placa}
                  stroke={CORES_LINHAS[i % CORES_LINHAS.length]}
                  connectNulls dot isAnimationActive={false}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="card">
          <h2>Status dos motoristas</h2>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={dadosStatus} dataKey="value" nameKey="name" outerRadius={90} label>
                {dadosStatus.map((d) => (
                  <Cell key={d.name} fill={CORES_STATUS[d.name] ?? '#6b7280'} />
                ))}
              </Pie>
              <Legend />
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </section>
    </div>
  )
}
