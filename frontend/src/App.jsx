import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Agents from './pages/Agents'
import AgentCreate from './pages/AgentCreate'
import APIConfigs from './pages/APIConfigs'
import Tests from './pages/Tests'
import TestCreate from './pages/TestCreate'
import TestDetail from './pages/TestDetail'
import TestResults from './pages/TestResults'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/agents" element={<Agents />} />
        <Route path="/agents/create" element={<AgentCreate />} />
        <Route path="/apis" element={<APIConfigs />} />
        <Route path="/tests" element={<Tests />} />
        <Route path="/tests/create" element={<TestCreate />} />
        <Route path="/tests/:id" element={<TestDetail />} />
        <Route path="/tests/:id/results" element={<TestResults />} />
      </Routes>
    </Layout>
  )
}

export default App
