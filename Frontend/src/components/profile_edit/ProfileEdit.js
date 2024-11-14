import React, { useEffect, useState } from 'react';
import { useNavigate } from "react-router-dom";
import { Card, Divider, Form, Input, message, Upload, Avatar,  Tabs, theme } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import "./style.css"


const ProfileEdit = () => {
    let navigate = useNavigate();
    const [form] = Form.useForm();
    const [messageApi, contextHolder] = message.useMessage();
    const { TextArea } = Input;
    const {
        token: { colorBgContainer, borderRadiusLG },
      } = theme.useToken();
      const [userInfo, setUserInfo] = useState({
        userId: '',
        nickName: '',
        avatar: '',
        createdAt: '',
        isBanned: false,          // Domyślnie false, jeśli nie jest zwrócone
        banExpirationDate: '',
    });

        const request_user_info = async (userId) => {
            try {
                const response = await fetch(`http://localhost:8001/forum/users/whoami?userId=${userId}`);
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                const data = await response.json();
    
                // Ustawienie informacji o użytkowniku z domyślnymi wartościami dla brakujących pól
                setUserInfo({
                    userId: data.userId || '',
                    nickName: data.nickName || '',
                    avatar: data.avatar || '',
                    createdAt: Math.floor((new Date() - new Date(data.createdAt)) / (1000 * 60 * 60))  || '',
                    isBanned: data.isBanned || false,
                    banExpirationDate: new Date(data.banExpirationDate).toLocaleDateString() || '',
                });
            } catch (error) {
                console.error('Error fetching user info:', error);
            }
        };
    
      useEffect(() => {
        request_user_info("doman4")
      }, [])
      


    return (
        <>
            {contextHolder}
            <div className='flex flex-col items-center overflow-auto'>
                <ul className='mt-10'>
                <div style={{ display: 'flex', alignItems: 'flex-end', marginBottom: '2px'}}>
                    <Avatar
                        size={160}
                        shape="square"
                        src={userInfo.avatar}
                        style={{
                            border: '3px solid #a6adb4',
                            cursor: 'pointer'
                        }}
                    />
                    <div>
                        {userInfo?.isBanned ? (<p style={{ marginLeft: '16px' }} className='text-red-600 font-semibold'>User is banned until {userInfo.banExpirationDate}</p>):(<></>)}
                        <h2 className='text-white font-bold text-3xl' style={{ marginLeft: '16px' }}>
                            {userInfo.nickName}
                        </h2>
                        <h2 className='font-bold text-1xl' style={{ marginLeft: '16px', color:"#a6adb4" }}>
                            Joined {userInfo.createdAt} hours ago
                        </h2>
                    </div>
                    
                    
                    
                </div>
                <Divider style={{width:"800px", marginTop: '2px'}}/>
                    <Tabs
                        defaultActiveKey="1"
                        theme="dark"
                        size='large'
                        style={{color:"white"}}
                    >
                        <Tabs.TabPane tab="Posts" key="1" style={{color:"white"}}>
                            Tab 1
                        </Tabs.TabPane>
                        <Tabs.TabPane tab="Comments" key="2">
                            Tab 2
                        </Tabs.TabPane>
                        <Tabs.TabPane tab="Upvoted" key="3">
                            Tab 3
                        </Tabs.TabPane>
                        <Tabs.TabPane tab="Downvoted" key="4">
                            Tab 3
                        </Tabs.TabPane>
                        <Tabs.TabPane tab="Communities" key="5">
                            Tab 3
                        </Tabs.TabPane>
                    </Tabs>
                </ul>
            </div>
        </>
    );
};

export default ProfileEdit;