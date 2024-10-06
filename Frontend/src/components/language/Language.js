import React from 'react'
import { Button } from 'antd'
import {ReactComponent as Polish} from '../../assets/Polish.svg';
import {ReactComponent as UK} from '../../assets/UK.svg';
import {ReactComponent as German} from '../../assets/German.svg';
import {ReactComponent as Spanish} from '../../assets/Spanish.svg';
import { useNavigate } from "react-router-dom";


const Language = () => {
let navigate = useNavigate();


  function handle_language() {
    return navigate("/");
  }
  return (
    <div className='flex flex-col items-center justify-center w-screen h-screen'>
        <h1 className='text-4xl font-semibold text-white mb-10'>Select language</h1>
        <Button className='flow-root ' onClick={handle_language} style={{
                            width: '323px',
                            height: '74px',
                            borderRadius: "100px",
                            overflow: "hidden",
                            backgroundColor: "white",
                            marginBottom: '24px'
                             }} type="primary">

                <p className='float-right pt-1 pr-[110px] text-2xl font-semibold text-[#446FB1]'>Polski</p>
                <div className='pr-4 float-left'>
                <Polish/>
                </div>
        </Button>
        <Button className='flow-root ' onClick={handle_language} style={{
                            width: '323px',
                            height: '74px',
                            borderRadius: "100px",
                            overflow: "hidden",
                            backgroundColor: "white",
                            marginBottom: '24px'
                             }} type="primary">

                <p className='float-right pt-1 pr-[102px] text-2xl font-semibold text-[#446FB1]'>English</p>
                <div className='pr-4 float-left'>
                <UK/>
                </div>
        </Button>
        <Button className='flow-root ' onClick={handle_language} style={{
                            width: '323px',
                            height: '74px',
                            borderRadius: "100px",
                            overflow: "hidden",
                            backgroundColor: "white",
                            marginBottom: '24px'
                             }} type="primary">

                <p className='float-right pt-1 pr-[94px] text-2xl font-semibold text-[#446FB1]'>Deutsch</p>
                <div className='pr-4 float-left'>
                <German/>
                </div>
        </Button>
        <Button className='flow-root ' onClick={handle_language} style={{
                            width: '323px',
                            height: '74px',
                            borderRadius: "100px",
                            overflow: "hidden",
                            backgroundColor: "white",
                            marginBottom: '24px'
                             }} type="primary">

                <p className='float-right pt-1 pr-[94px]  text-2xl font-semibold text-[#446FB1]'>Español</p>
                <div className='pr-4 float-left'>
                <Spanish/>
                </div>
        </Button>
    </div>
  )
}

export default Language