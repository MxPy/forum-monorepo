import React, { useState, useEffect } from 'react';
import { 
  LaptopOutlined, NotificationOutlined, UserOutlined, 
  MessageOutlined, BellOutlined, CaretDownOutlined, CaretUpOutlined,
  BorderlessTableOutlined, SettingOutlined, LogoutOutlined,
  HomeOutlined, RiseOutlined, FireOutlined, GlobalOutlined
} from '@ant-design/icons';

import { Breadcrumb, Layout, Menu, theme, Button, Divider, Flex, Radio, Space, Dropdown, Badge, Avatar } from 'antd';
import LandingPage from '../components/landing_page/LandingPage';
import ProfileEdit from '../components/profile_edit/ProfileEdit';

const { Header, Content, Sider } = Layout;

const communities = [{name:'React Devs', logo:"http://localhost:9000/logos/ComfyUI_00284_.png"}, {name:'Vue Enthusiasts', logo:"http://localhost:9000/logos/zaj.jpg"}, {name:'Angular Coders', logo:"http://localhost:9000/logos/ert.jpg"}, {name:'Svelte Fans', logo:"http://localhost:9000/logos/kitku.png"}];

const handleEditClick = () => console.log('Edit clicked');
const handleAddClick = () => console.log('Add clicked');
const handleNotificationClick = () => console.log('Notification clicked');
const handleAvatarClick = () => console.log('Avatar clicked');

const dropdownMenu = (
  <Menu theme="dark" style={{ backgroundColor: "#001529" }}>
    <Menu.Item key="profile" icon={<UserOutlined />} style={{ color: '#a6adb4' }}>Profile</Menu.Item>
    <Menu.Item key="settings" icon={<SettingOutlined />} style={{ color: '#a6adb4' }}>Settings</Menu.Item>
    <Menu.Divider style={{ backgroundColor: '#a6adb4' }} />
    <Menu.Item key="logout" icon={<LogoutOutlined />} style={{ color: '#a6adb4' }}>Logout</Menu.Item>
  </Menu>
);

const GlobalLayout = () => {
  const [isCommunitiesOpen, setIsCommunitiesOpen] = useState(true);
  const toggleCommunities = () => setIsCommunitiesOpen(prev => !prev);
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
    bannedByAdminId: ''       // Pusty string, jeśli nie jest zwrócone
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
            createdAt: data.createdAt || '',
            isBanned: data.isBanned || false,
            banExpirationDate: data.banExpirationDate || '',
            bannedByAdminId: data.bannedByAdminId || ''
        });
        console.log(userInfo)
    } catch (error) {
        console.error('Error fetching user info:', error);
    }
  };

  useEffect(() => {
    request_user_info("doman4")
  }, [])
  
  useEffect(() => {
    console.log(userInfo)
  }, [userInfo])
  
  


  return (
    <Layout style={{ height: '100vh', overflow: 'hidden' }}>
      <Header style={{ display: 'flex', alignItems: 'center', height: '80px', position: 'sticky', top: 0, zIndex: 1, padding: '0 24px', border: '1px solid #2e2157' }}>
        <div className="demo-logo" style={{ width: '240px', height: '60px', borderRadius: '6px' }}>
          <img src="images/logo.png" alt="logo"></img>
        </div>
        <Menu theme="dark" mode="horizontal" selectedKeys={[]} className="ml-auto min-w-0 flex items-center" style={{ gap: '0' }}
          items={[
            {
              key: 'sub1',
              icon: <Badge size="small" count={8}><BorderlessTableOutlined style={{ fontSize: '24px' }} /></Badge>,
              onClick: handleEditClick,
              style: { backgroundColor: 'transparent', display: 'flex', alignItems: 'center', margin: '0', padding: '0 8px' },
            },
            {
              key: 'sub2',
              icon: <Badge size="small" count={8}><MessageOutlined style={{ fontSize: '24px' }} /></Badge>,
              onClick: handleEditClick,
              style: { backgroundColor: 'transparent', display: 'flex', alignItems: 'center', margin: '0', padding: '0 8px' },
            },
            {
              key: 'sub3',
              icon: <Badge size="small" count={1}><BellOutlined style={{ fontSize: '24px' }} /></Badge>,
              onClick: handleNotificationClick,
              style: { backgroundColor: 'transparent', display: 'flex', alignItems: 'center', margin: '0', padding: '0 8px' },
            },
            {
              key: 'sub4',
              icon: (
                <Dropdown theme='dark' overlay={dropdownMenu} trigger={['click']} placement="bottomRight">
                  <Avatar size={48} shape="square" src={userInfo.avatar} style={{ display: 'flex', alignItems: 'center', border: '3px solid #a6adb4', cursor: 'pointer' }} />
                </Dropdown>
              ),
              style: { backgroundColor: 'transparent', display: 'flex', alignItems: 'center', padding: '0 0 0 8px', margin: '0' },
            }
          ]}
        />
      </Header>
      <Layout>
        <Sider width={300} style={{ background: colorBgContainer, height: 'calc(100vh - 64px)', overflow: 'auto' }}>
          <Menu theme="dark" mode="inline" selectedKeys={[]} style={{ height: '100%', borderRight: 0, border: '1px solid #2e2157' }}>
            <Menu.Item key="home" icon={<HomeOutlined style={{ fontSize: '24px' }} />} onClick={handleEditClick}>Home</Menu.Item>
            <Menu.Item key="popular" icon={<RiseOutlined style={{ fontSize: '24px' }} />} onClick={handleEditClick}>Popular</Menu.Item>
            <Menu.Item key="explore" icon={<GlobalOutlined style={{ fontSize: '24px' }} />} onClick={handleEditClick}>Explore</Menu.Item>
            <Menu.Item key="new" icon={<FireOutlined style={{ fontSize: '24px' }} />} onClick={handleEditClick}>New</Menu.Item>
            <Menu.Divider style={{ backgroundColor: '#2e2157', height: '2px' }} />
            <Menu.Item key="communities" icon={isCommunitiesOpen ? <CaretDownOutlined style={{ fontSize: '14px' }} /> : <CaretUpOutlined style={{ fontSize: '14px' }} />} onClick={toggleCommunities}>Communities</Menu.Item>
            {isCommunitiesOpen && communities.map((community, index) => (
              <Menu.Item key={`community-${index}`} style={{ paddingLeft: '24px' }}><Avatar size={30} shape="square" src={community.logo} style={{ marginRight:'5px', display: 'flex', alignItems: 'center', border: '1px solid #a6adb4', cursor: 'pointer' }} />{community.name}</Menu.Item>
            ))}
          </Menu>
        </Sider>
        <Layout>
          <Content style={{ overflow: 'auto', background: 'linear-gradient(#2e2157, #540d6e)' }}>
            <div style={{ height: '100%', overflow: 'auto' }}>
              {/* <LandingPage /> */}
              <ProfileEdit/>
            </div>
          </Content>
        </Layout>
      </Layout>
    </Layout>
  );
};

export default GlobalLayout;
