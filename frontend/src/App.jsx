import { useEffect, useMemo, useState } from 'react'
import { MapContainer, TileLayer, CircleMarker, Circle, Popup, useMap } from 'react-leaflet'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts'
import 'leaflet/dist/leaflet.css'
import './App.css'

/* ----------------------------------------------------------------------------------- */
/* DADOS FAKE. Depois serão trocados por chamadas à API do backend com axios.get(...)  */
/* ----------------------------------------------------------------------------------- */
const MOTORISTAS = [
  { id: 1, nome: 'Carlos Andrade', cnh: '123456789', status: 'Ativo' },
  { id: 2, nome: 'Mariana Silva', cnh: '987654321', status: 'Ativo' },
  { id: 3, nome: 'Roberto Souza', cnh: '456789123', status: 'Em Descanso' },
]

const VEICULOS = [
  { id: 101, placa: 'ABC-1A23', modelo: 'Volvo FH 540', motorista_id: 1 },
  { id: 102, placa: 'XYZ-9876', modelo: 'Scania R450', motorista_id: 2 },
  { id: 103, placa: 'KGB-4567', modelo: 'Mercedes Actros', motorista_id: 3 },
]

// ATENÇÃO: no GeoJSON a ordem é [longitude, latitude].
// O Leaflet usa o contrário: [latitude, longitude]. Por isso convertemos abaixo.
const TELEMETRIA = [
  { veiculo_id: 101, coordinates: [-34.873, -7.115], temperatura: 4.2, velocidade: 65, timestamp: '2026-09-11T10:00:00Z' },
  { veiculo_id: 102, coordinates: [-34.832, -7.121], temperatura: -18.5, velocidade: 85, timestamp: '2026-09-11T10:05:00Z' },
  { veiculo_id: 103, coordinates: [-34.95, -7.15], temperatura: 22.0, velocidade: 0, timestamp: '2026-09-11T09:45:00Z' },
]

const PONTOS_REFERENCIA = [
  { nome: 'Centro (João Pessoa)', lat: -7.115, lng: -34.873 },
  { nome: 'Cabo Branco', lat: -7.121, lng: -34.832 },
  { nome: 'Tibiri / BR-230', lat: -7.15, lng: -34.95 },
]

const LIMITE_VELOCIDADE = 80
const CORES_STATUS = { Ativo: '#16a34a', 'Em Descanso': '#f59e0b' }

/* Distância em km entre dois pontos (fórmula de Haversine).
   Por enquanto o cálculo é feito aqui; no projeto final quem filtra
   é o MongoDB com $near / $geoWithin. */
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

// Faz o mapa "voar" para o novo ponto quando o usuário troca a referência.
function Recentralizar({ centro }) {
  const map = useMap()
  useEffect(() => {
    map.setView(centro)
  }, [centro, map])
  return null
}

export default function App() {
  const [refIndex, setRefIndex] = useState(0)
  const [raioKm, setRaioKm] = useState(10)

  const referencia = PONTOS_REFERENCIA[refIndex]
  const centro = [referencia.lat, referencia.lng]

  // "Join poliglota em memória": junta SQLite (motorista, veículo) + MongoDB (telemetria)
  const frota = useMemo(() => {
    return TELEMETRIA.map((t) => {
      const veiculo = VEICULOS.find((v) => v.id === t.veiculo_id)
      const motorista = MOTORISTAS.find((m) => m.id === veiculo?.motorista_id)
      const [lng, lat] = t.coordinates
      return {
        veiculo_id: t.veiculo_id,
        motorista: motorista?.nome ?? '—',
        status: motorista?.status ?? '—',
        placa: veiculo?.placa ?? '—',
        modelo: veiculo?.modelo ?? '—',
        temperatura: t.temperatura,
        velocidade: t.velocidade,
        lat,
        lng,
        distancia: distanciaKm(referencia.lat, referencia.lng, lat, lng),
      }
    })
  }, [referencia])

  const dentroDoRaio = frota.filter((v) => v.distancia <= raioKm)

  // KPIs
  const frotasAtivas = frota.filter((v) => v.status === 'Ativo').length
  const mediaTemp = frota.reduce((soma, v) => soma + v.temperatura, 0) / frota.length
  const alertas = frota.filter((v) => v.velocidade > LIMITE_VELOCIDADE).length

  // Gráfico de pizza: distribuição do status dos motoristas
  const dadosStatus = Object.entries(
    MOTORISTAS.reduce((acc, m) => ({ ...acc, [m.status]: (acc[m.status] ?? 0) + 1 }), {}),
  ).map(([name, value]) => ({ name, value }))

  return (
    <div className="app">
      <header>
        <h1>GeoLog · LogiTech Express</h1>
        <p>Monitoramento de frota em tempo real</p>
      </header>

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
          <Recentralizar centro={centro} />
          <TileLayer
            attribution="&copy; OpenStreetMap"
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <Circle center={centro} radius={raioKm * 1000} pathOptions={{ color: '#2563eb', fillOpacity: 0.08 }} />
          <CircleMarker center={centro} radius={6} pathOptions={{ color: '#111', fillColor: '#111', fillOpacity: 1 }}>
            <Popup>Referência: {referencia.nome}</Popup>
          </CircleMarker>
          {frota.map((v) => {
            const dentro = v.distancia <= raioKm
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
                  A {v.distancia.toFixed(1)} km da referência
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
          <h2>Temperatura por veículo</h2>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={frota}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="placa" />
              <YAxis unit="°C" />
              <Tooltip />
              <Bar dataKey="temperatura" fill="#2563eb" />
            </BarChart>
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
