import '../../../shared/styles/App.css'
import Header from "../../navbar/components/Header"

export default function HomePage() {
  return (
    <main>
      <Header/>
      <div className="flex h-[90vh] w-full justify-center items-center ">
          <p className="text-white text-3xl"> Home Page </p>
      </div>
    </main>
  )
}