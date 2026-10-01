import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { api, WS_URL } from '../services/api'

/* O Mongo devolve datas sem fuso ("2026-09-11T10:00:00"). Sem o "Z" o JavaScript
   interpretaria como horário local e erraria 3h. Aqui forçamos UTC quando faltar. */
export function toMs(timestamp) {
  if (!timestamp) return 0
  const temFuso = /(Z|[+-]\d{2}:?\d{2})$/.test(timestamp)
  return new Date(temFuso ? timestamp : `${timestamp}Z`).getTime()
}

const jitter = (amplitude) => (Math.random() * 2 - 1) * amplitude

/**
 * Concentra tudo que fala com o backend:
 *  - GET  /motoristas, /veiculos, /telemetrias        (carga dos dados)
 *  - GET  /veiculos/proximos                          (busca por raio no MongoDB)
 *  - WS   /telemetrias/ws                             (atualizações em tempo real)
 *  - POST /telemetrias                                (simulador de movimentação)
 */
export function useGeoLog(referencia, raioKm) {
  const [motoristas, setMotoristas] = useState([])
  const [telemetrias, setTelemetrias] = useState([]) // histórico completo
  const [idsNoRaio, setIdsNoRaio] = useState(() => new Set())
  const [socketId, setSocketId] = useState(null)
  const [carregando, setCarregando] = useState(true)
  const [erro, setErro] = useState(null)
  const simulando = useRef(false)

  const carregar = useCallback(async () => {
    try {
      const [mot, tel] = await Promise.all([
        api.get('/api/v1/motoristas'),
        api.get('/api/v1/telemetrias'),
      ])
      setMotoristas(mot.data)
      setTelemetrias(tel.data)
      setErro(null)
    } catch (e) {
      console.error(e)
      setErro('Não foi possível carregar os dados. Verifique se a API está rodando.')
    } finally {
      setCarregando(false)
    }
  }, [])

  useEffect(() => {
    carregar()
  }, [carregar])

  /* WebSocket: o backend só envia telemetria nova de veículos que estão dentro do raio
     que registramos via /veiculos/proximos. O socket_id liga uma coisa à outra.
     Geramos um id novo a cada conexão (o StrictMode do React monta o efeito duas vezes). */
  useEffect(() => {
    const id = crypto.randomUUID()
    const ws = new WebSocket(`${WS_URL}/api/v1/telemetrias/ws?socket_id=${id}`)
    ws.onopen = () => setSocketId(id)
    ws.onclose = () => setSocketId(null)
    ws.onmessage = (evento) => {
      const nova = JSON.parse(evento.data)
      setTelemetrias((atual) => {
        const repetida = atual.some(
          (t) => t.veiculo.id === nova.veiculo.id && toMs(t.timestamp) === toMs(nova.timestamp),
        )
        return repetida ? atual : [nova, ...atual]
      })
    }
    return () => ws.close()
  }, [])

  /* Busca por raio: quem filtra é o MongoDB ($geoNear com índice 2dsphere).
     O debounce evita disparar uma requisição a cada pixel do slider.
     telemetrias.length está nas dependências para refazer a busca quando chegar dado novo. */
  useEffect(() => {
    if (!socketId) return
    const timer = setTimeout(async () => {
      try {
        const { data } = await api.get('/api/v1/veiculos/proximos', {
          params: {
            latitude: referencia.lat,
            longitude: referencia.lng,
            raio: raioKm,
            socket_id: socketId,
          },
        })
        setIdsNoRaio(new Set(data.map((t) => t.veiculo.id)))
        setErro(null)
      } catch (e) {
        console.error(e)
        setErro('Falha na busca por raio (/veiculos/proximos).')
      }
    }, 300)
    return () => clearTimeout(timer)
  }, [socketId, referencia, raioKm, telemetrias.length])

  // Última telemetria de cada veículo (a de maior timestamp).
  const ultimas = useMemo(() => {
    const mapa = new Map()
    for (const t of telemetrias) {
      const atual = mapa.get(t.veiculo.id)
      if (!atual || toMs(t.timestamp) > toMs(atual.timestamp)) mapa.set(t.veiculo.id, t)
    }
    return mapa
  }, [telemetrias])

  /* "Join poliglota": o backend já devolve cada telemetria (MongoDB) com o veículo e o
     motorista (SQLite) aninhados. Aqui só achatamos para o formato que a tela usa. */
  const frota = useMemo(
    () =>
      [...ultimas.values()].map((t) => ({
        veiculo_id: t.veiculo.id,
        motorista: t.veiculo.motorista.nome,
        status: t.veiculo.motorista.status,
        placa: t.veiculo.placa,
        modelo: t.veiculo.modelo,
        temperatura: t.temperatura,
        velocidade: t.velocidade,
        lat: t.location.latitude,
        lng: t.location.longitude,
        timestamp: t.timestamp,
      })),
    [ultimas],
  )

  // Bônus: gera novos pontos GPS com pequena variação aleatória e grava no MongoDB.
  const simularMovimentacao = useCallback(async () => {
    if (simulando.current) return
    simulando.current = true
    try {
      await Promise.all(
        [...ultimas.values()].map((t) =>
          api.post('/api/v1/telemetrias', {
            veiculo_id: t.veiculo.id,
            location: {
              latitude: t.location.latitude + jitter(0.005),
              longitude: t.location.longitude + jitter(0.005),
            },
            temperatura: Number((t.temperatura + jitter(1)).toFixed(1)),
            velocidade: Math.max(0, Math.round(t.velocidade + jitter(15))),
            timestamp: new Date().toISOString(),
          }),
        ),
      )
      await carregar()
    } catch (e) {
      console.error(e)
      setErro('Falha ao simular movimentação.')
    } finally {
      simulando.current = false
    }
  }, [ultimas, carregar])

  return {
    motoristas, telemetrias, frota, idsNoRaio,
    aoVivo: socketId !== null,
    carregando, erro, simularMovimentacao,
  }
}
